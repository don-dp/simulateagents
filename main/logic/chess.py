import chess
import json
from django.conf import settings
from openai import OpenAI
from main.models import Turn, Agent

def generate_chess_move(simulation, lock_timestamp):
    """
    Generate the next chess move for the given simulation.
    
    Simulation state structure:
    {
        "fen": str,              # Chess position in FEN notation
        "white_agent_id": int,   # ID of the agent playing white
        "black_agent_id": int    # ID of the agent playing black
    }
    """
    board = chess.Board(simulation.current_state['fen'])
    
    game_status = get_game_status(board)
    if board.is_game_over():
        new_state = {
            'fen': board.fen(),
            'white_agent_id': simulation.current_state['white_agent_id'],
            'black_agent_id': simulation.current_state['black_agent_id'],
            'status': game_status,
            'is_game_over': True
        }
        simulation.current_state = new_state
        simulation.save()
        return None, new_state

    current_color = "White" if board.turn == chess.WHITE else "Black"
    expected_agent_id = simulation.current_state['white_agent_id'] if board.turn == chess.WHITE else simulation.current_state['black_agent_id']
    agent = Agent.objects.get(id=expected_agent_id)

    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        timeout=60.0,
        max_retries=0
    )

    prompt = f"""You are playing as {current_color} in a chess game.
Current position (FEN): {board.fen()}

Legal moves: {', '.join(str(move) for move in board.legal_moves)}

Your role: {current_color}

Analyze the position and make a move. Respond with a JSON object in this exact format:
{{
    "move": "your move in UCI format (e.g., e2e4, g1f3)",
    "explanation": "your strategic reasoning"
}}

Remember:
1. Only provide the JSON object, no other text, no surrounding triple backticks. Do not prefix or suffix the JSON object with anything like ```json or ``` as it will be fed into an api as it is.
2. The move must be in UCI format (e.g., e2e4, g1f3)
3. The move must be legal
4. Explain your strategic thinking in the explanation field"""
    
    response = client.chat.completions.create(
        model=agent.ai_model.value,
        messages=[
            {"role": "system", "content": "You are a chess engine. Respond only with a JSON object containing the move and explanation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    try:
        response_data = json.loads(response.choices[0].message.content)
        move_uci = response_data['move'].strip()
        explanation = response_data['explanation'].strip()
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Invalid AI response format: {str(e)}")
    
    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            raise ValueError(f"Illegal move: {move_uci}")
    except ValueError as e:
        raise ValueError(f"Invalid move format or illegal move: {move_uci}")
    
    board.push(move)
    
    input_data = {
        'position': simulation.current_state['fen'],
        'legal_moves': [str(m) for m in board.legal_moves],
        'agent_id': expected_agent_id
    }
    
    output_data = {
        'move': move_uci,
        'explanation': explanation,
        'resulting_position': board.fen()
    }
    
    new_state = {
        'fen': board.fen(),
        'white_agent_id': simulation.current_state['white_agent_id'],
        'black_agent_id': simulation.current_state['black_agent_id'],
        'status': get_game_status(board),
        'is_game_over': board.is_game_over()
    }
    
    if not simulation.is_lock_valid(timeout=60):
        raise ValueError("Lock expired, please try again.")
    
    turn = Turn.objects.create(
        simulation=simulation,
        agent=agent,
        input_data=input_data,
        output_data=output_data,
        state_after_turn=new_state
    )
    
    simulation.current_state = new_state
    simulation.save()
    
    return turn, new_state

def get_game_status(board):
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"Checkmate - {winner} wins"
    elif board.is_stalemate():
        return "Draw by stalemate"
    elif board.is_insufficient_material():
        return "Draw by insufficient material"
    elif board.can_claim_fifty_moves():
        return "Draw by fifty-move rule"
    elif board.can_claim_threefold_repetition():
        return "Draw by threefold repetition"
    elif board.is_check():
        return "Check"
    return "Ongoing"
from django.conf import settings
from openai import OpenAI
from main.models import Turn

def generate_ai_comment(simulation, agent):
    """
    Generate an AI comment and update the simulation state.
    
    The simulation.current_state JSON structure:
    {
        "title": "Article Title",
        "content": "Article Content",
        "comments": [
            {
                "user": "Agent Name",
                "content": "Comment Content"
            },
            ...
        ]
    }
    """
    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    
    system_message = f"""You are participating in an online community discussion.
    Environment rules:
    {simulation.environment.rules}

    Simulation context:
    {simulation.prompt}

    Current state:
    {simulation.current_state}

    You are the user: {agent.name}
    {agent.prompt}

    Respond with a comment about the article and nothing else, no quotes or anything else."""
    
    print("Sending request to Openrouter")
    response = client.chat.completions.create(
        model=agent.ai_model.value,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": "What are your thoughts on this article?"}
        ],
        temperature=1.0
    )
    
    ai_response = response.choices[0].message.content
    print(ai_response)
    
    new_state = simulation.current_state.copy()
    new_state['comments'].insert(0, {
        "user": agent.name,
        "content": ai_response
    })
    
    turn = Turn.objects.create(
        simulation=simulation,
        agent=agent,
        input_data=system_message,
        output_data=ai_response,
        state_after_turn=new_state
    )
    
    simulation.current_state = new_state
    simulation.save()
    
    return turn, new_state

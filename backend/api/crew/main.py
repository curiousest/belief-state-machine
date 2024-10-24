from .crew import ExtractBeliefsWriteParableCrew, WriteParableCrew, BeliefLayer


def extract_beliefs(text, context) -> BeliefLayer:
    result = ExtractBeliefsWriteParableCrew(text=text, context=context).crew().kickoff()
    return result

def write_parable(belief: str, action: str, text: str, context: str) -> str:
    '''
    Write a parable that challenges the belief to be the action.
    action: "changed" or "reinforced" or "meaningless"
    '''
    result = WriteParableCrew(belief=belief, action=action, text=text, context=context).crew().kickoff()
    return result



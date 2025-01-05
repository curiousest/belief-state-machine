from crew import ExtractBeliefsWriteParableCrew, WriteParableCrew

result = ExtractBeliefsWriteParableCrew().crew().kickoff()

target_belief = result.to_dict()['beliefs'][0]

result = WriteParableCrew(belief=target_belief).crew().kickoff()

print("===================== Final Result ===================================")
print(result)

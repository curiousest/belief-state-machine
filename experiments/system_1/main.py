from crew import ExtractBeliefsWriteParableCrew, WriteParableCrew

# todo
# make the input text and context come from somewhere else

# debug why the parables suck
# 1. Try other files/context to see if it's the input
# 2. Compare against manual text entry to see if it's the api/model
# 3. Compare different models for parable generation to see if it's the model

# make it interactive - pick the belief and what kind of change to generate a parable for
# make it "minimum viable belief change" - build a tree of beliefs and operate on the ones that are lowest-level with no overlapping dependencies above them
# ex: rome had a strong military and rome's culture incoporated military values => go one level higher 

# make it a web app 
# - upload/paste files and context
# - filter prompt injection



# add a bit of memory to the webapp?

result = ExtractBeliefsWriteParableCrew().crew().kickoff()

target_belief = result.to_dict()['beliefs'][0]

result = WriteParableCrew(belief=target_belief).crew().kickoff()

print("===================== Final Result ===================================")
print(result)

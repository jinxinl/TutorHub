import os
import pandas as pd
import openai
import time
import json
import re

openai_client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY",""),
    base_url=os.environ.get("OPENAI_BASE_URL","https://svip.xty.app/v1")
)

def get_json_response_from_gpt(
    messages,
    model='gpt-4o-mini',
    temperature=0.7,
    max_tokens=4096,
    need_keys=[],
    max_retries=20
):
    if 'ckpt' in model:
        pass
    else:
        client = openai_client

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content        
        json_dict = json.loads(content)
        return json_dict
    
    except Exception as e:
        if "This model's maximum context length is " in str(e):
            raise e
        print(f"Exception occurs: {e}")
        max_retries -= 1
        if max_retries <= 0:
            raise e
        
def extract_python_block(text:str) -> str:
    pattern = r"```(?:python)?\s*([\s\S]*?)\s*```"
    matches = re.findall(pattern, text)
    return matches[-1] if matches else ""
        
def extrac_relation(intro:str,model="gpt-4o-2024-11-20",max_retries=15):
    intro_str = json.dumps(intro,ensure_ascii=False,indent=4)
    prompt = f"""You are a relation extraction assistant. You will be given a dictionary, where each dictionary contains two keys:
- "Name": The name of a teacher.
- "Introduction": A brief introduction of the teacher.

Your task is to extract the following information from the "Introduction" field and return a JSON object:
1. The mentorship relationships (mentors).
2. The graduate school(s) the teacher attended.

The result should be a JSON object with the following keys:
- "Name": The name of the teacher.
- "Tutors": A list of the teacher's mentors (if no mentors are mentioned, return an empty list).
- "Graduate_school": A list of the teacher's graduate schools (if no graduate schools are mentioned, return an empty list).

Please ensure:
1. Only explicitly mentioned mentorship relationships and graduate schools are extracted.
2. If no mentors or graduate schools are mentioned in the "Introduction", the corresponding value should be an empty list.
3. The result should be a JSON object, formatted as follows:
```python
{{
    "Name": "Teacher A",
    "Tutors": ["Mentor 1", "Mentor 2"],
    "Graduate_school": ["School 1", "School 2"]
}}
```
Here is the text to process:
{intro_str}"""
    
    messages = [
        {"role":"system","content":"You are a helpful assistant."},
        {"role":"user","content":prompt}
    ]    

    retries = 0
    while retries <= max_retries:
        try:
            output = get_json_response_from_gpt(model=model,messages=messages)
            print(f"output\n{output}")
            if isinstance(output,dict):
                    if "Name" in output.keys() and "Tutors" in output.keys() and "Graduate_school" in output.keys():
                        print("Successfully extract mentorship relationships")
                        return output
                    else:
                        print(f"Missing key. Retrying... (Attempt {retries + 1}/{max_retries}).")    
                        retries += 1
                        time.sleep(1.5 * (2**retries))             
            else:
                print(f"GPT response is not well formatted. Retrying... (Attempt {retries + 1}/{max_retries})")
                retries += 1
                time.sleep(1.5 * (2**retries))

        except Exception as e:
            print(f"Error: {e}. Retrying... (Attempt {retries + 1}/{max_retries})")
            retries += 1
            time.sleep(1.5 * (2**retries))

def convert_files(file_path:str,mf_path:str,af_path:str):
    origin_data = pd.read_json(file_path)
    origin_data =origin_data.to_dict(orient="record")
    mentorships,graduate_schools = {},{}

    for data in origin_data:
        if len(data["Tutors"]):
            mentorships[f"{data['Name']}"] = data["Tutors"]

        for school in data["Graduate_school"]:
            if school in graduate_schools.keys():
                graduate_schools[school].append(data["Name"])
            else:
                graduate_schools[school] = [data["Name"]]
    
    with open(mf_path,"w",encoding="utf-8") as f:
        json.dump(mentorships,f,ensure_ascii=False,indent=4)
    with open(af_path,"w",encoding="utf-8") as f:
        json.dump(graduate_schools,f,ensure_ascii=False,indent=4)
    
    
def main():
    print("Loading tutor basic information")
    data = pd.read_json("TutorBasic.json")

    print("Extracting mentorship relationships")
    intros = [{"Name":d["Name"],"Introduction":d["Introduction"]} for d in data.to_dict(orient='records')]
    relations = []
    for intro in intros:
        # 调用模型逐个解析导师个人简介    
        result = extrac_relation(intro=intro,model="gpt-4o-2024-11-20",max_retries=15)
        relations.append(result)
    
    # 保存模型提取信息
    with open("Relationships.json","w",encoding="utf-8") as f:
        json.dump(relations,f,ensure_ascii=False,indent=4)
    print("Successfully save relation extracting information as JSON file")

    # 整理并保存师承关系和校友关系
    convert_files(file_path="Relationships.json",mf_path="TutorRelation.json",af_path="AlumniRelations.json")
    print("Successfully saved mentorships and alumni relationships as JSON files")


if __name__ == "__main__":
    main()
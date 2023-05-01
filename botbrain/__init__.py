import cohere
import json
import pandas as pd
from botbrain.utils import API_KEY
from cohere.responses.classify import Example


# uses the input/examples.csv files as the example set
class BotBrain:
    cohere_obj : cohere.Client
    examples : list
    model : str
    lang_supported : dict


    def __init__(self, model:str):
        self.cohere_obj = cohere.Client(f"{API_KEY}")
        self.model = model
        self.examples = self._get_examples()
        lang_file = open("data/supportedlang.json")
        lang_data = lang_file.read()
        lang_file.close()
        self.lang_supported = json.loads(lang_data)
        # print(type(self.lang_supported))


    def _get_examples(self):
        data_dict = pd.read_csv('input/examples.csv').to_dict()
        result_ = []
        for i in range(len(data_dict["issue_title"])):
            result_.append(
                Example(data_dict["issue_title"][i], data_dict["label"][i])
            ) 
        return result_


    def label_issues(self, github_issues_list:list):
        if len(self.examples) == 0:
            # Throws an error if the example set is empty
            return None
        else:
            response = self.cohere_obj.classify(
                inputs=github_issues_list,
                examples=self.examples,
                model=self.model
            )
            return response


    def translate_issues(self):
        return {}

 
import cohere
import json
import pandas as pd
from botbrain.utils import API_KEY
from cohere.responses.classify import Example


# uses the input/examples.csv files as the example set
class BotBrain:
    cohere_obj: cohere.Client
    examples: list
    model: str
    lang_supported: dict

    def __init__(self, model: str):
        self.cohere_obj = cohere.Client(f"{API_KEY}")
        self.model = model
        self.examples = self._get_examples()
        lang_file = open("botbrain/data/supportedlang.json")
        lang_data = lang_file.read()
        lang_file.close()
        self.lang_supported = json.loads(lang_data)
        self.confidence_threshold = .7

    def _get_examples(self):
        print("Debug")
        data_dict = pd.read_csv('botbrain/input/examples.csv').to_dict()
        result_ = []
        for i in range(len(data_dict["issue_title"])):
            result_.append(
                Example(data_dict["issue_title"][i], data_dict["label"][i])
            )
        return result_

    def label_issues(self, github_issues_list: list):
        if len(self.examples) == 0:
            return None
        else:
            print(f"{github_issues_list}; {self.examples}; {self.model}")
            response = self.cohere_obj.classify(
                inputs=github_issues_list,
                examples=self.examples,
                model=self.model
            )
            predicted_labels = [label.prediction for label in response]
            result = []
            for i in range(len(predicted_labels)):
                result.append((github_issues_list[i], predicted_labels[i]))
            return result

    def predict_label_from_issues(self, issue, issue_samples) -> str:
        # issue -> issue_title+issue_body
        # issue_samples -> [(issue_title + issue_body, label),...]
        samples = [Example(content, label) for content, label in issue_samples]
        response = self.cohere_obj.classify(
            inputs=[issue],
            examples=samples,
            model=self.model
        )

        classifications = response.classifications
        score = classifications[0]['confidence']
        if score < self.confidence_threshold:
            return ''

        return classifications[0]['prediction']

    def translate_issue(self, issue_title, issue_body, lang: str) -> str:
        if lang not in self.lang_supported:
            return f"Sorry couldn't figure out how to translate to {lang.capitalize()}"

        prompt = f"rewrite quoted text in {lang}: \"{issue_body}\""
        response = self.cohere_obj.generate(
            model= self.model,
            prompt=prompt,
            max_tokens=450,
            temperature=0.9
        )
        lang_detect = self.cohere_obj.detect_language([response.generations[0].text])
        lang_in_cap = lang.capitalize()
        if all(language.language_name == lang_in_cap for language in lang_detect.results):
            return "\n".join(response.texts)

        return f"Sorry couldn't figure out how to translate to {lang.capitalize()}"



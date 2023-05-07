import cohere
import json
import pandas as pd
from cohere.responses.classify import Example
from collections import Counter


# uses the input/examples.csv files as the example set
class BotBrain:
    cohere_obj: cohere.Client
    examples: list
    model: str
    lang_supported: dict

    def __init__(self, model: str, api_key=""):
        self.cohere_obj = cohere.Client(api_key)
        self.model = model
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

    def predict_label_from_issues(self, issue, issue_samples, issue_labels) -> str:
        # issue -> issue_title+issue_body
        # issue_samples -> [(issue_title + issue_body, label),...]
        samples = [Example(content, label) for content, label in issue_samples]
        unique_labels = Counter(issue_labels)
        filtered_samples = list(filter(lambda sample: unique_labels[sample.label] > 1, samples))
        try:
            response = self.cohere_obj.classify(
                inputs=[issue],
                examples=filtered_samples,
                model=self.model
            )

            classifications = response.classifications
            score = classifications[0].confidence
            print(f"score: {score}")
            if score < self.confidence_threshold:
                return ''

            return classifications[0].prediction
        except Exception as exc:
            print(exc)
        return ''

    def translate_issue(self, issue_title, issue_body, lang: str) -> str:
        if lang not in self.lang_supported:
            return f"Sorry couldn't figure out how to translate to {lang.capitalize()}"

        prompt = f"rewrite quoted text in {lang}: \"{issue_title} {issue_body}\""
        response = self.cohere_obj.generate(
            model=self.model,
            prompt=prompt,
            max_tokens=450,
            temperature=0.9
        )
        lang_detect = self.cohere_obj.detect_language([response.generations[0].text])
        lang_in_cap = lang.capitalize()
        if all(language.language_name == lang_in_cap for language in lang_detect.results):
            return "\n".join(response.generations[0].text.split('\r\n'))

        return f"Sorry couldn't figure out how to translate to {lang.capitalize()}"

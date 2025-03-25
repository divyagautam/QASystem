"""
    This file conatins the Logging class defined here
    for logging prompts and responses during the LLM call.
    The output is dumped in the outputs folder, which can
    be used during Human evaluation and bookkeeping. 
"""
import json
from typing import Dict, List, Any

from langchain_core.callbacks import BaseCallbackHandler

all_output = []
def convert_to_dict(obj):
    if isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return convert_to_dict(obj.__dict__)
    elif isinstance(obj, list):
        return [convert_to_dict(item) for item in obj]
    else:
        return obj

# custom callback to save the final prompt sent to the llm and the response
class LoggingCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], run_id, metadata, name, **kwargs) -> None:
        global all_output
        all_output.append({
                "name": serialized.get('name'),
                "run_id": str(run_id),
                "prompt": inputs,
                "metdata": metadata
            })

    def on_llm_end(self, response, *, run_id, parent_run_id = None, **kwargs):
        global all_output
        result = response.__dict__
        all_output[-1]["response"] = convert_to_dict(result['generations'])

        # dump all_output to json file
        with open("./outputs/llm_outputs.json", "w") as f:
            json.dump(all_output, f, indent=2)
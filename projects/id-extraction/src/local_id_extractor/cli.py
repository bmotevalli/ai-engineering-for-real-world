import argparse
import sys

from . import ExtractionError, Extractor, ImageInputError
from .ollama import ALLOWED_MODELS, DEFAULT_MODEL, OllamaBackend
from .prompts import DEFAULT_PROMPT, PROMPTS


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a local identity image to validated JSON")
    parser.add_argument("image")
    parser.add_argument("--model", choices=ALLOWED_MODELS, default=DEFAULT_MODEL)
    parser.add_argument("--prompt", choices=PROMPTS, default=DEFAULT_PROMPT)
    parser.add_argument("--context", type=int, choices=(4096, 8192), default=4096)
    args = parser.parse_args()
    try:
        result = Extractor(OllamaBackend(args.model, context_length=args.context), prompt=args.prompt).extract(args.image)
    except (ExtractionError, ImageInputError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(result.model_dump_json(indent=2))
    return 0

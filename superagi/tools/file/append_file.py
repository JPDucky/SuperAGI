import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool

import tweepy


class AppendFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to write")
    content: str = Field(..., description="The text to append to the file")


class AppendFileTool(BaseTool):
    name: str = "append_file"
    args_schema: Type[BaseModel] = AppendFileInput
    description: str = "Append text to a file"

    def execute(self, file_name: str, content: str):
        final_path = file_name
        root_dir = os.getenv('RESOURCES_ROOT_DIR')
        if root_dir is not None:
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + file_name
        else:
            final_path = os.getcwd() + "/" + file_name
        try:
            directory = os.path.dirname(final_path)
            os.makedirs(directory, exist_ok=True)
            with open(final_path, 'a', encoding="utf-8") as file:
                file.write(content)
            return "File written to successfully."
        except Exception as err:
            return f"Error: {err}"

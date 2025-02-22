from fluxion_ai.core.modules.llm_modules import DeepSeekR1ChatModule

class TogetherAIChatModule(DeepSeekR1ChatModule):

    def __init__(self, *args, response_key="choices", **kwargs):
        super().__init__(*args, response_key=response_key, **kwargs)

    def post_process(self, response, full_response = False):
        output = super(DeepSeekR1ChatModule, self).post_process(response, full_response)[-1]["message"]
        if self.remove_thinking_tag_content and "content" in output:
            output["content"] = self.remove_thinking(output["content"])
        return output
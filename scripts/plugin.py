# 导入必要的库和模块
import contextlib
from re import S
import gradio as gr  # Gradio用于构建Web界面
from diffusers.pipelines import StableDiffusionPipeline  # Stable Diffusion管道
#, StableDiffusionXLPipeline  # pylint: disable=unused-import
from modules import shared, scripts, processing, sd_models, devices  # WebUI核心模块

# 导入处理相关类
from modules.processing import (
    StableDiffusionProcessing,  # 基础处理类
    StableDiffusionProcessingImg2Img,  # 图生图处理类
    create_infotext,  # 创建信息文本
    process_images,  # 处理图像
    Processed,  # 处理结果
)
import subprocess  # 用于调用外部程序
import json  # 处理JSON数据




def send_text_to_prompt(new_text, old_text):
    if old_text == "":  # if text on the textbox text2img or img2img is empty, return new text
        return new_text
    return old_text + "," + new_text  # else join them together and send it to the textbox


class Script(scripts.Script):
    def title(self):
        return "sd-chenx"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def _call_external_script(self, script_path, params):
        print("开始调用外部脚本6666")
        try:
            # 根据文件后缀选择解释器
            if script_path.endswith('.py'):
                cmd = ["python", script_path, json.dumps(params)]
                print("cmd", cmd)
            elif script_path.endswith('.js'):
                cmd = ["node", script_path, json.dumps(params)]
            elif script_path.endswith('.exe'):
                cmd = [script_path, json.dumps(params)]
            else:
                return ""
                
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print("执行完成，输出：")
            return process.stdout
        except subprocess.CalledProcessError as e:
            print(f"脚本执行失败：{e.stderr}")
            return ""


    def ui(self, _is_img2img):
        with gr.Group():
            with gr.Accordion('动态py插件', open=False):
                enabled = gr.Checkbox(
                    value=False, label='开启插件', elem_id=id('enabled'))
                
                # 添加外部脚本调用相关UI元素
                with gr.Row():
                    script_path = gr.Textbox(label="脚本路径", placeholder="输入Python/Node.js/C#程序路径")
                    input_params = gr.Textbox(label="输入参数", placeholder="输入参数(可选)")
                
                with gr.Row():
                    text_to_be_sent = gr.Textbox(label="追加要发送的文本",visible=False)
                    send_text_button = gr.Button("发送文本",variants="primary",visible=False)
                    

                # uicheckbox = []
                # uicheckbox.insert(0, enabled)
                # uicheckbox.append(script_path)
                # uicheckbox.append(input_params)
        with contextlib.suppress(AttributeError):
            if _is_img2img:
                send_text_button.click(fn=send_text_to_prompt, inputs=[text_to_be_sent, self.boxxIMG], outputs=[self.boxxIMG])
            else:
                send_text_button.click(fn=send_text_to_prompt, inputs=[text_to_be_sent, self.boxx], outputs=[self.boxx])

        uicheckbox=[]
        uicheckbox.append(enabled)
        uicheckbox.append(text_to_be_sent)
        uicheckbox.append(send_text_button)
        uicheckbox.append(input_params)
        uicheckbox.append(script_path)

        return uicheckbox


    def after_component(self, component, **kwargs):
        #https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/7456#issuecomment-1414465888 helpfull link
        # Find the text2img textbox component
        if kwargs.get("elem_id") == "txt2img_prompt": #postive prompt textbox
            self.boxx = component
        # Find the img2img textbox component
        if kwargs.get("elem_id") == "img2img_prompt":  #postive prompt textbox
            self.boxxIMG = component

    def process(self, p: StableDiffusionProcessing, *args):
        """
        对于AlwaysVisible脚本，在处理开始前调用此函数。
        你可以在这里修改处理对象(p)，注入钩子等。
        args包含ui()中组件返回的所有值
        """
        print("argsddd", args)
        enabled = args[0]
        input_params = args[3]
        script_path = args[4]

        print("script_path", script_path)
        print("input_params", input_params)
        print("enabled", enabled)

        if enabled:
            print("调用外部脚本")
            try:
                if input_params=="":
                    input_params = ""
                else:
                    input_params = '{"input_params": "'+input_params+'"}'

                params = json.loads(input_params) if input_params else {}
                #把p的所有参数和值加到params
                # for key, value in p.__dict__.items():
                #     params[key] = value
                # print("params", params)
                result = self._call_external_script(script_path, params)
                print(f"外部脚本执行结果: {result}")
                
                resjson=json.loads(result)

                addstr=""
                if resjson.get("allprompt"):
                    addstr=resjson.get("allprompt")
                    if hasattr(p, 'all_prompts') and addstr != "":
                        addstr=addstr.strip()
                        if not any(addstr in s for s in p.all_prompts):
                            p.all_prompts[0]=p.all_prompts[0]+","+addstr

                addstr=""
                if resjson.get("allneoprompt"):
                    addstr=resjson.get("allneoprompt")
                    if hasattr(p, 'all_negative_prompts') and addstr != "":
                        addstr=addstr.strip()

                        if not any(addstr in s for s in p.all_negative_prompts):
                            p.all_negative_prompts[0]=p.all_negative_prompts[0]+","+addstr


                print("p.all_prompts", p.all_prompts)
                print("p.all_negative_prompts", p.all_negative_prompts)


            except Exception as e:
                print(f"调用外部脚本出错: {str(e)}")

        #this code below  works aswell, you can send negative prompt text box,provided you change the code a little
        #switch  self.boxx with  self.neg_prompt_boxTXT  and self.boxxIMG with self.neg_prompt_boxIMG

        #if kwargs.get("elem_id") == "txt2img_neg_prompt":
            #self.neg_prompt_boxTXT = component
        #if kwargs.get("elem_id") == "img2img_neg_prompt":
            #self.neg_prompt_boxIMG = component

    # def run(self, p, *args):
    #     """
    #     当脚本在下拉菜单中被选中时调用此函数。
    #     必须完成所有处理并返回与processing.process_images返回的相同的Processed对象。
    #     通常通过调用processing.process_images函数来完成处理。
    #     args包含ui()中组件返回的所有值
    #     """
    #     enabled = args[0]
    #     script_path = args[1]
    #     input_params = args[2]
        
    #     if enabled and script_path:
    #         try:
    #             params = json.loads(input_params) if input_params else {}
    #             result = self._call_external_script(script_path, params)
    #             print(f"外部脚本执行结果: {result}")
    #         except Exception as e:
    #             print(f"调用外部脚本出错: {str(e)}")
    #     pass

    # def setup(self, p, *args):
    #     """
    #     对于AlwaysVisible脚本，在设置处理对象时调用此函数，在任何处理开始之前。
    #     args包含ui()中组件返回的所有值。
    #     """
    #     pass

    # def before_process(self, p, *args):
    #     """
    #     对于AlwaysVisible脚本，在处理开始时很早就调用此函数。
    #     你可以在这里修改处理对象(p)，注入钩子等。
    #     args包含ui()中组件返回的所有值
    #     """
    #     pass



    # def before_process_batch(self, p, *args, **kwargs):
    #     """
    #     在从提示词解析额外网络之前调用，因此你可以通过此回调向提示词添加新的额外网络关键词。

    #     **kwargs将包含以下项目：
    #       - batch_number - 当前批次的索引，从0到批次数量-1
    #       - prompts - 当前批次的提示词列表；你可以更改此列表的内容，但更改条目数量可能会导致问题
    #       - seeds - 当前批次的种子列表
    #       - subseeds - 当前批次的子种子列表
    #     """
    #     pass

    # def after_extra_networks_activate(self, p, *args, **kwargs):
    #     """
    #     在额外网络激活后，条件计算之前调用
    #     允许在应用额外网络激活后修改网络
    #     如果p.disable_extra_networks为真则不会调用

    #     **kwargs将包含以下项目：
    #       - batch_number - 当前批次的索引，从0到批次数量-1
    #       - prompts - 当前批次的提示词列表；你可以更改此列表的内容，但更改条目数量可能会导致问题
    #       - seeds - 当前批次的种子列表
    #       - subseeds - 当前批次的子种子列表
    #       - extra_network_data - 当前阶段的ExtraNetworkParams列表
    #     """
    #     pass

    # def process_before_every_sampling(self, p, *args, **kwargs):
    #     """
    #     类似于process()，在每次采样之前调用。
    #     如果使用高分辨率修复，这将被调用两次。
    #     """
    #     pass

    # def process_batch(self, p, *args, **kwargs):
    #     """
    #     与process()相同，但为每个批次调用。

    #     **kwargs将包含以下项目：
    #       - batch_number - 当前批次的索引，从0到批次数量-1
    #       - prompts - 当前批次的提示词列表；你可以更改此列表的内容，但更改条目数量可能会导致问题
    #       - seeds - 当前批次的种子列表
    #       - subseeds - 当前批次的子种子列表
    #     """
    #     pass

    # def postprocess_batch(self, p, *args, **kwargs):
    #     """
    #     与process_batch()相同，但在生成每个批次后调用。

    #     **kwargs将包含与process_batch相同的项目，以及：
    #       - batch_number - 当前批次的索引，从0到批次数量-1
    #       - images - 包含所有生成图像的torch张量，值范围从0到1
    #     """
    #     pass

    # def postprocess_batch_list(self, p, pp: PostprocessBatchListArgs, *args, **kwargs):
    #     """
    #     与postprocess_batch()相同，但接收批次图像作为3D张量列表而不是4D张量。
    #     当你想要更新整个批次而不是单个图像时，这很有用。

    #     你可以修改后处理对象(pp)来更新批次中的图像，删除图像，添加图像等。
    #     如果返回时图像数量与批次大小不同，
    #     那么脚本有责任同时更新处理对象(p)中的以下属性：
    #       - p.prompts
    #       - p.negative_prompts
    #       - p.seeds
    #       - p.subseeds

    #     **kwargs将包含与process_batch相同的项目，以及：
    #       - batch_number - 当前批次的索引，从0到批次数量-1
    #     """
    #     pass

    # def on_mask_blend(self, p, mba: MaskBlendArgs, *args):
    #     """
    #     在修复模式下，当原始内容与修复内容混合时调用。
    #     这在去噪过程的每一步都会调用，并在最后调用一次。
    #     如果is_final_blend为真，则这是为最终混合阶段调用的。
    #     否则，denoiser和sigma已定义，可用于指导过程。
    #     """
    #     pass

    # def post_sample(self, p, ps: PostSampleArgs, *args):
    #     """
    #     在生成样本后，但在它们被VAE解码之前调用（如果适用）。
    #     检查getattr(samples, 'already_decoded', False)以测试图像是否已解码。
    #     """
    #     pass

    # def postprocess_image(self, p, pp: PostprocessImageArgs, *args):
    #     """
    #     在生成每个图像后调用。
    #     """
    #     pass

    # def postprocess_maskoverlay(self, p, ppmo: PostProcessMaskOverlayArgs, *args):
    #     """
    #     在生成每个图像后调用。
    #     """
    #     pass

    # def postprocess_image_after_composite(self, p, pp: PostprocessImageArgs, *args):
    #     """
    #     在生成每个图像后调用。
    #     与postprocess_image相同，但在inpaint_full_res合成之后
    #     因此它在完整图像上操作，而不是在inpaint_full_res裁剪区域上操作。
    #     """
    #     pass

    # def postprocess(self, p, processed, *args):
    #     """
    #     对于AlwaysVisible脚本，在处理结束后调用此函数。
    #     args包含ui()中组件返回的所有值
    #     """
    #     pass

    # def before_component(self, component, **kwargs):
    #     """
    #     在创建组件之前调用。
    #     使用kwargs的elem_id/label字段来确定是哪个组件。
    #     这对于在原始UI中间注入自己的组件很有用。
    #     你可以在ui()函数中返回创建的组件，将它们添加到处理函数的参数列表中
    #     """
    #     pass




    # def on_before_component(self, callback, *, elem_id):
    #     """
    #     在创建组件之前调用回调。回调函数使用OnComponent类型的单个参数调用。

    #     可以在show()或ui()中调用 - 但在后者中可能太晚，因为一些组件可能已经创建。

    #     这个函数是before_component的替代方案，它也允许在创建组件之前运行，
    #     但不需要为每个创建的组件调用 - 只需要为你需要的组件调用。
    #     """
    #     if self.on_before_component_elem_id is None:
    #         self.on_before_component_elem_id = []

    #     self.on_before_component_elem_id.append((elem_id, callback))

    # def on_after_component(self, callback, *, elem_id):
    #     """
    #     在创建组件后调用回调。回调函数使用OnComponent类型的单个参数调用。
    #     """
    #     if self.on_after_component_elem_id is None:
    #         self.on_after_component_elem_id = []

    #     self.on_after_component_elem_id.append((elem_id, callback))

    # def describe(self):
    #     """未使用"""
    #     return ""

    # def elem_id(self, item_id):
    #     """
    #     辅助函数，用于生成HTML元素的id，从脚本名称、标签页和用户提供的item_id构造最终id
    #     """
    #     need_tabname = self.show(True) == self.show(False)
    #     tabkind = 'img2img' if self.is_img2img else 'txt2img'
    #     tabname = f"{tabkind}_" if need_tabname else ""
    #     title = re.sub(r'[^a-z_0-9]', '', re.sub(r'\s', '_', self.title().lower()))

    #     return f'script_{tabname}{title}_{item_id}'

    # def before_hr(self, p, *args):
    #     """
    #     在高分辨率修复开始之前调用此函数。
    #     """
    #     pass
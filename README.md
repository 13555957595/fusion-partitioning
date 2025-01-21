# PDF-Processor

##系通过以下命令安装magic-pdf组件###

    pip install -U magic-pdf[full] --extra-index-url https://wheels.myhloli.com -i https://mirrors.aliyun.com/pypi/simple

##需要配置magic-pdf.json的环境变量###

    export MINERU_TOOLS_CONFIG_JSON=your_magic_pdf.json

###模型路径需要修改 修改项目中的mgic-pdf.json文件###


###注意模型目录是该项目的huggingface目录，由于模型太大没法上传到gitee，请联系开发人员获取最新的模型###

    "models-dir": "C:\\Users\\Administrator\\.cache\\huggingface\\hub\\models--opendatalab--PDF-Extract-Kit-1.0\\snapshots\\fcf59ee2de3dad2dc35fbeeb0e35779f288cee9c/models",
    "layoutreader-model-dir": "C:\\Users\\Administrator\\.cache\\huggingface\\hub\\models--hantian--layoutreader\\snapshots\\641226775a0878b1014a96ad01b9642915136853",


###如果需要gpu加速，请执行以下命令####

    pip install --force-reinstall torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cu118

###修改magic-pdf.json中的###

      {
        "device-mode":"cuda"
      }

###测试magic-pdf,请执行以下命令验证工具是否执行###
        
    magic-pdf -p ./pdf/456.pdf -o ./pdf/output
     
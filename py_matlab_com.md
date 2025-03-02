# 连接 Python 和 MATLAB/Simulink

## 介绍
本文档提供了一个将 Python 与 MATLAB/Simulink 集成的基本框架。此集成允许利用两种环境的优势进行高级数据分析、可视化和仿真。

## 目录
- [介绍](#介绍)
- [Python 环境准备](#python-环境准备)
- [安装](#安装)
    - [安装 MATLAB Engine API for Python](#安装-matlab-engine-api-for-python)
- [基本用法](#基本用法)
    - [启动 MATLAB 引擎](#启动-matlab-引擎)
    - [调用 MATLAB 函数](#调用-matlab-函数)
    - [停止 MATLAB 引擎](#停止-matlab-引擎)
- [示例：运行 Simulink 模型](#示例运行-simulink-模型)
- [结论](#结论)
- [参考资料](#参考资料)


## Python 环境准备
首先，我们准备一个隔离好的Python环境，如果需要使用`venv`新建并进入一个名为`matlab_env`的环境，可按照过程操作：

```bash
cd <targetLocation>

# Create a virtual environment
python -m venv matlab_env

# Activate on Windows
matlab_env\Scripts\activate
```

随后，设置并查看相关环境变量`PYTHONPATH`

```bash
# Set `PYTHONPATH` (in a Windows shell)
set PYTHONPATH=%VIRTUAL_ENV%/lib/python3.x/site-packages:%PYTHONPATH%

# Verify it
echo %PYTHONPATH%
```



## 安装

### 安装 MATLAB Engine API for Python
要安装 MATLAB Engine API for Python，请按照以下步骤操作：

1. 打开命令提示符。
2. 在Matlab命令行下执行下述命令：
    ```sh
    strcat(matlabroot, '/extern/engines/python')
    ```
3. 随后导航到这一目录，并运行安装指令：
    ```sh
    python setup.py install
    ```
4. 最后检查库是否成功安装，执行`pip list`应看到有`matlabengineforpython`库组件及其对应版本号。

## 基本用法

### 启动 MATLAB 引擎
要从 Python 启动 MATLAB 引擎，请使用以下代码：
```python
import matlab.engine
eng = matlab.engine.start_matlab()
```

### 调用 MATLAB 函数
您可以直接从 Python 调用 MATLAB 函数。例如：
```python
result = eng.sqrt(4.0)
print(result)  # 输出: 2.0
```

### 停止 MATLAB 引擎
要停止 MATLAB 引擎，请使用以下代码：
```python
eng.quit()
```

## 示例：运行 Simulink 模型
以下是如何从 Python 运行 Simulink 模型的示例：
```python
import matlab.engine
eng = matlab.engine.start_matlab()
eng.load_system('model_name')
eng.sim('model_name')
eng.quit()
```

## 结论
将 Python 与 MATLAB/Simulink 集成可以通过结合两种环境的功能来增强您的工作流程。本文档提供了设置和使用此集成的起点。

## 参考资料
- [MATLAB Engine API for Python 文档](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html)
- [Simulink 文档](https://www.mathworks.com/help/simulink/)
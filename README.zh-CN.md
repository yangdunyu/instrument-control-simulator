# 仪器控制模拟器

[English](README.md) | [简体中文](README.zh-CN.md)

一个轻量级光学测试仪器模拟框架。
项目实现了 SCPI 命令解析、仪器状态管理、firmware 升级生命周期，以及基于 FastAPI 和 React 的实时状态界面。

---

## 架构

```mermaid
flowchart TD
    A["Presentation Layer<br/>Frontend / Cohesion-style UI<br/><br/>用户点击按钮，例如 Power On / Set Power / Measure"]
    --> B["API Layer<br/>Backend REST API<br/><br/>接收请求、参数校验、返回结构化结果"]

    B --> C["Framework Layer<br/>InstrumentService / Registry<br/><br/>定义统一业务动作：<br/>connect(), power_on(), power_off(), set_power(), measure(), get_status()"]

    C --> D["Adapter Layer<br/>LaserAdapter<br/><br/>根据不同设备，把统一动作翻译成设备能听懂的 SCPI 命令；<br/>抹平不同设备之间的差异"]

    D --> E["Protocol Layer<br/>SCPIProtocol<br/><br/>负责发送命令、接收响应，并提供 transport 边界；<br/>未来可替换为 TCP / USB / VISA / Vendor SDK"]

    E --> F["Device Layer<br/>LaserDevice Simulator<br/><br/>执行命令，保存状态，返回状态、测量值或错误码"]

    F --> E
    E --> D
    D --> C
    C --> B
    B --> A
```

---

## 项目功能

### 仪器发现与连接
- 通过 `GET /api/instruments` 暴露仪器注册表，模拟局域网仪器发现
- 支持单台仪器 connect / disconnect
- 连接成功后返回 `*IDN?` 设备身份字符串

### SCPI 命令控制台
- 支持 10 条 SCPI-like 命令
- React UI 显示命令历史、时间戳和响应结果
- 支持功率范围校验、输出状态校验和未知命令错误
- 使用确定性错误模拟真实控制问题，例如输出未开启、参数越界、未知命令

### 结构化仪器 API
- 为常用激光控制提供高层 endpoint：输出开关、设置功率、读取测量功率
- 后端 `LaserAdapter` 将语义化调用映射到原始 SCPI 命令
- React 控制面板使用结构化 API，同时保留 raw SCPI command console

**支持命令：**

| 命令 | 说明 |
|------|------|
| `*IDN?` | 查询仪器身份 |
| `SYST:VERS?` | 查询 firmware 版本 |
| `SOUR:POW <val>` | 设置输出功率，范围 -60 到 +10 dBm |
| `SOUR:POW?` | 查询当前功率设置 |
| `OUTP ON / OFF` | 打开 / 关闭输出 |
| `OUTP?` | 查询输出状态 |
| `MEAS:POW?` | 测量当前功率，要求输出已开启 |
| `SYST:ERR?` | 查询最近错误 |
| `*RST` | 重置仪器状态 |

### Firmware 升级生命周期
- 生命周期：`idle -> uploading -> validating -> applying -> completed`
- 前端通过 `GET /api/instruments/{id}/firmware/status` 轮询升级进度
- 确定性完成，不再使用随机失败率

### SCPI Script Runner
- 通过 `POST /api/instruments/{id}/script` 执行多行 SCPI 脚本
- 自动忽略空行和 `#` 注释，并返回逐步 pass/fail 结果
- 适合模拟自动化验证流程，例如 connect -> configure -> enable output -> measure

### 可扩展仪器框架
- `InstrumentBase` 抽象类定义统一接口
- 新仪器类型可继承 `InstrumentBase`，不需要修改 API 层
- `InstrumentService`、`LaserAdapter`、`SCPIProtocol`、`LaserDevice` 明确对应框架分层
- API 路由、registry/service、adapter 翻译、protocol transport、device state 分离

### 自动化测试
- **27 个 pytest 测试**：12 个 SCPI 单元测试 + 12 个 API 集成测试 + 3 个分层测试
- **3 个 Playwright e2e 场景**：连接仪器、发送命令、firmware 升级

### 开发体验
- `docker compose up` 一键启动
- GitHub Actions CI：pytest -> frontend build -> Playwright -> Docker build
- C++17 standalone driver mock，使用 CMake 编译，stdin/stdout 交互

---

## 快速启动

```bash
docker compose up
# Backend:  http://localhost:8000
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
```

### 本地开发

```bash
# Terminal 1: backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: frontend
cd frontend
npm install
npm run dev
```

### 运行测试

```bash
# Backend pytest
cd backend && pytest tests/ -v

# Frontend Playwright
cd frontend && npx playwright test
```

### 构建 C++ driver

```bash
cd cpp-driver
mkdir build && cd build
cmake ..
cmake --build .
echo "*IDN?" | ./instrument_driver
```

---

## 分层映射

| 层 | 实现 |
|----|------|
| Presentation | `frontend/src/App.tsx`、React components |
| API | `backend/app/main.py` |
| Framework | `backend/app/simulator/instrument_service.py` |
| Adapter | `backend/app/simulator/laser_adapter.py` |
| Protocol | `backend/app/simulator/scpi_protocol.py` |
| Device | `backend/app/simulator/laser_device.py` |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| Backend | Python 3.12, FastAPI, Pydantic |
| Frontend | React 18, TypeScript, Vite |
| Testing | pytest, Playwright |
| DevOps | Docker, GitHub Actions |
| Driver mock | C++17, CMake |

## 简历项目 Features

- 搭建包含 API、Framework、Adapter、Protocol、Device 的可复用仪器控制模拟框架。
- 实现 registry-based 仪器发现与连接管理，支持 `*IDN?` 身份校验和单仪器 session 状态维护。
- 开发 SCPI-style 命令解析器，覆盖功率设置、输出开关、测量读取、重置、firmware 版本查询和错误查询等控制流程。
- 封装 `LaserAdapter` 结构化仪器控制层，将 `set_power`、`power_on`、`power_off`、`measure` 等语义化操作映射到原始 SCPI 命令。
- 设计 firmware 升级生命周期，支持进度轮询、版本更新和并发冲突处理。
- 构建 React + TypeScript 控制界面，包含仪器发现、结构化激光控制、raw SCPI console、命令历史和 firmware 进度展示。
- 增加 newline-delimited SCPI script runner，返回逐步 pass/fail 报告，并实现输入校验与连接状态约束。
- 使用 27 个 pytest 测试和 3 个 Playwright e2e 场景覆盖后端逻辑、API 集成和核心 UI 流程。
- 配置 Docker Compose 本地环境与 GitHub Actions CI，覆盖 backend tests、frontend build、e2e tests 和 Docker image validation。
- 实现 C++17 standalone driver mock，使用 CMake 构建并通过 stdin/stdout 处理控制命令，展示跨语言仪器控制能力。

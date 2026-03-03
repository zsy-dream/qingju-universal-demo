# 青居智算｜Universal System 启动指南

> 本项目为基于 Hedonic 模型的高校毕业生租房防坑与真实估值系统（前后端分离全栈工程）。

---

## 工程结构（按提示词固定目录）

```text
Universal_System/
├── backend/                  # FastAPI + SQLite
│   ├── app/
│   │   ├── api/v1/endpoints/ # 接口层
│   │   ├── core/             # 配置/DB/安全
│   │   ├── models/           # SQLAlchemy ORM
│   │   ├── schemas/          # Pydantic 校验
│   │   └── services/         # 业务逻辑
│   ├── data/                 # SQLite 数据库（自动创建）
│   ├── logs/
│   ├── .env                  # 环境变量
│   └── requirements.txt
└── frontend/                 # Vue3 + Vite + TailwindCSS
    ├── src/
    │   ├── api/              # Axios 封装
    │   ├── components/       # 通用高颜值组件
    │   ├── layouts/
    │   ├── views/            # Dashboard/Estimate/Risk
    │   ├── router/
    │   └── styles/
    ├── index.html
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.js
```

---

## 一、后端启动（FastAPI + SQLite）

### 1) 安装依赖（Windows 示例）

```powershell
# 进入后端目录
cd Universal_System\backend

# 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2) 启动服务

```powershell
# 在 backend 目录下执行
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3) 验证

- 服务地址：`http://localhost:8000`
- 交互式文档：`http://localhost:8000/docs`（Swagger UI）

---

## 二、前端启动（Vue3 + Vite + Tailwind）

### 1) 安装依赖

```powershell
# 进入前端目录
cd Universal_System\frontend

# 安装依赖（若提示 npm 未找到，先安装 Node.js LTS）
npm install
```

### 2) 启动开发服务器

```powershell
# 在 frontend 目录下执行
npm run dev
```

### 3) 验证

- 前端地址：`http://localhost:5173`
- 默认自动代理到后端：`/api/*` → `http://localhost:8000`

---

## 三、联调端口与跨域

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 (Vite) | 5173 | 开发服务器，带热更新 |
| 后端 (FastAPI) | 8000 | API 服务，CORS 已放行 `http://localhost:5173` |

跨域已配置：
- 后端 `app/core/config.py`：`CORS_ORIGINS=http://localhost:5173`
- 前端 `vite.config.js`：已配置 `proxy: { '/api': { target: 'http://localhost:8000' } }`

---

## 四、快速演示路径

1. 前后端都启动后，打开前端 `http://localhost:5173`
2. 点击右上角「一键注入演示房源」写入两条示例数据
3. 进入「驾驶舱」查看估值偏离趋势与最新房源
4. 进入「真实估值」页面，输入房源信息，点击「执行估值」查看区间与因素贡献
5. 进入「防坑风控」页面，设置风险信号（0/1/2），生成风控结论与建议动作

---![alt text](image.png)

## 五、注意事项（Windows 常见）

- **SQLite 路径**：若出现数据库文件创建失败，检查 `.env` 中 `SQLITE_DB_PATH` 是否为相对路径 `./data/app.db`，或改为绝对路径如 `D:/.../data/app.db`。
- **端口占用**：若 8000/5173 被占用，修改启动命令或 `.env` / `vite.config.js` 中的端口。
- **依赖缺失**：若后端提示 `ModuleNotFoundError`，确认已激活虚拟环境并执行 `pip install -r requirements.txt`。

---

## 六、后端分层约定（必读）

| 层 | 职责 | 示例文件 |
|----|------|----------|
| **endpoints** | 仅接收请求、参数校验、调用 Service、返回结果 | `endpoints/assessments.py` |
| **services** | 业务逻辑、AI 调用、算法计算、数据库操作 | `services/assessment_service.py` |
| **schemas** | Pydantic 请求/响应结构 | `schemas/assessment.py` |
| **models** | SQLAlchemy ORM 模型 | `models/listing.py` |

---

## 七、前端风格（已选定）

**风格 C：赛博黑科技风**
- 色调：深黑(`#0B1220`) + 霓虹紫(`#8B5CF6`) + 流光粉(`#EC4899`)
- 特征：呼吸灯、HUD 面板、玻璃拟态(Glassmorphism)、发光边框、扫描线、流光 Skeleton
- 对标：`https://uiverse.io/` 高赞组件（NeonButton/GlassCard）

---

## 八、下一步扩展（可选）

- **估值模型**：当前为简化 Hedonic-like 逻辑，可扩展为真实 Hedonic 回归或接入外部数据源。
- **证据上传**：已实现证据表，可扩展文件上传与预览。
- **议价话术**：已预留模块，可接入模板引擎或 LLM 生成。
- **租后闭环**：已预留事件时间线结构，可扩展记录与维权辅助。

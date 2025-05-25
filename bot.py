from flask import Flask, request, jsonify, render_template_string
import threading
import time
import uuid
import requests

app = Flask(__name__)

active_tasks = {}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>FB Automation Panel</title>
<style>
  body {
    font-family: Arial, sans-serif;
    background: #121212;
    color: #eee;
    margin: 0; padding: 0;
  }
  nav {
    background: #1abc9c;
    display: flex;
    gap: 20px;
    padding: 15px 30px;
  }
  nav a {
    color: white;
    text-decoration: none;
    cursor: pointer;
    font-weight: bold;
  }
  nav a:hover {
    text-decoration: underline;
  }
  section {
    max-width: 600px;
    margin: 20px auto;
    background: #222;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 0 15px #1abc9c;
  }
  img.admin-pic {
    display: block;
    margin: 0 auto 15px;
    border-radius: 50%;
    width: 150px;
    height: 150px;
    border: 4px solid #1abc9c;
    object-fit: cover;
  }
  h1, h2 {
    text-align: center;
    color: #1abc9c;
  }
  form label {
    display: block;
    margin-top: 15px;
    font-weight: bold;
  }
  input[type="text"],
  input[type="number"],
  input[type="file"] {
    width: 100%;
    padding: 8px;
    margin-top: 6px;
    border-radius: 6px;
    border: none;
  }
  input[type="submit"] {
    margin-top: 25px;
    background: #1abc9c;
    border: none;
    color: #121212;
    font-weight: bold;
    font-size: 1.1em;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
    width: 100%;
  }
  input[type="submit"]:hover {
    background: #16a085;
  }
  .tabs {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-bottom: 20px;
  }
  .tab {
    cursor: pointer;
    padding: 10px 25px;
    background: #333;
    border-radius: 8px;
    color: #bbb;
    font-weight: bold;
    user-select: none;
    transition: background 0.3s, color 0.3s;
  }
  .tab.active {
    background: #1abc9c;
    color: #121212;
  }
  .accordion-item {
    background: #1a1a1a;
    margin-bottom: 8px;
    border-radius: 6px;
  }
  .accordion-header {
    padding: 10px 15px;
    cursor: pointer;
    font-weight: bold;
    color: #1abc9c;
    user-select: none;
  }
  .accordion-content {
    display: none;
    padding: 15px;
  }
  .accordion-content.active {
    display: block;
  }
  .task button {
    background: #e74c3c;
    border: none;
    color: white;
    padding: 8px 12px;
    cursor: pointer;
    border-radius: 6px;
  }
  footer {
    text-align: center;
    margin-top: 60px;
    padding: 20px;
    background: #1a1a1a;
    color: #1abc9c;
    font-weight: bold;
    border-top: 1px solid #333;
  }
</style>
</head>
<body>

<nav>
  <a onclick="showSection('home')">Home</a>
  <a onclick="showSection('servers')">Servers</a>
  <a onclick="showSection('active_tasks')">Active Tasks</a>
</nav>

<section id="home" class="active">
  <img src="https://i.ibb.co/WWndrD0T/481767414-970935001810491-6220678936190020954-n.jpg" alt="Admin Picture" class="admin-pic" />
  <h1>𓆤『٭❲ 𝐀𝐫̽͜ɣ𝐚͢͡ŋ — ː › 🩶 🪽 </h1>
  <p style="text-align:center; font-style: italic; color:#aaa;">
    Web DeveLoper And Owner oFF SarFU Rullex [#] .
  </p>
  <p style="text-align:center; font-weight:bold; background:#1abc9c; padding:12px; border-radius:10px; width: fit-content; margin: 20px auto;">
    Total Tasks Created: <span id="totalTasks">0</span>
  </p>
</section>

<section id="servers" style="display:none;">
  <div class="tabs">
    <div id="tabConvo" class="tab" onclick="toggleTab('convo')">Start Convo</div>
    <div id="tabPost" class="tab" onclick="toggleTab('post')">Start Post</div>
  </div>

  <div id="convoSection" class="accordion-content">
    <div id="convoTasksAccordion"></div>
    <form id="convoForm">
      <label>Tokens File:</label>
      <input type="file" name="tokens" required />
      <label>Target UID:</label>
      <input type="text" name="target_uid" required />
      <label>Hatter Name:</label>
      <input type="text" name="hatter" required />
      <label>Message File:</label>
      <input type="file" name="messages" required />
      <label>Speed (sec):</label>
      <input type="number" step="0.1" name="speed" required />
      <label>Convo Name:</label>
      <input type="text" name="task_name" required />
      <input type="submit" value="Start Convo" />
    </form>
    <p style="text-align:center; color:#aaa; margin-top:20px; font-style:italic;">
      Start real conversations that shake the silence. 🚀
    </p>
  </div>

  <div id="postSection" class="accordion-content">
    <div id="postTasksAccordion"></div>
    <form id="postForm">
      <label>Cookies File:</label>
      <input type="file" name="cookies" required />
      <label>Target Post ID:</label>
      <input type="text" name="target_post" required />
      <label>Resume Post ID (optional):</label>
      <input type="text" name="resume_post" />
      <label>Hatter Name:</label>
      <input type="text" name="hatter" required />
      <label>Message File:</label>
      <input type="file" name="messages" required />
      <label>Delay (sec):</label>
      <input type="number" step="0.1" name="delay" required />
      <label>Post Name:</label>
      <input type="text" name="task_name" required />
      <input type="submit" value="Start Post" />
    </form>
    <p style="text-align:center; color:#aaa; margin-top:20px; font-style:italic;">
      Leave your mark on every post — make your presence legendary. 🌟
    </p>
  </div>
</section>

<section id="active_tasks" style="display:none;">
  <h2>Active Tasks</h2>
  <div id="tasksContainer">
    <p>No active tasks yet.</p>
  </div>
</section>

<footer>
  Made WiTh bYe ArYan.x3 UrF SarFu Rullex 2019 @ 2022
</footer>

<script>
  let totalTasks = 0;
  const tasks = [];

  function showSection(id) {
    if (id === "servers") {
      const password = prompt("Enter password to access Servers:");
      if (password !== "ArYan.x3") {
        alert("Access Denied. Wrong Password!");
        return;
      }
    }

    document.querySelectorAll("section").forEach(sec => {
      sec.style.display = "none";
      sec.classList.remove("active");
    });
    document.getElementById(id).style.display = "block";
    document.getElementById(id).classList.add("active");
  }

  function toggleTab(tab) {
    const convoTab = document.getElementById("tabConvo");
    const postTab = document.getElementById("tabPost");
    const convoSection = document.getElementById("convoSection");
    const postSection = document.getElementById("postSection");

    if (tab === "convo") {
      if(convoSection.classList.contains("active")) {
        convoSection.classList.remove("active");
        convoTab.classList.remove("active");
      } else {
        convoSection.classList.add("active");
        convoTab.classList.add("active");
        postSection.classList.remove("active");
        postTab.classList.remove("active");
      }
    } else if (tab === "post") {
      if(postSection.classList.contains("active")) {
        postSection.classList.remove("active");
        postTab.classList.remove("active");
      } else {
        postSection.classList.add("active");
        postTab.classList.add("active");
        convoSection.classList.remove("active");
        convoTab.classList.remove("active");
      }
    }
  }

  function toggleAccordion(event) {
    const header = event.currentTarget;
    const content = header.nextElementSibling;
    content.classList.toggle("active");
  }

  function addTaskToAccordion(task, index, containerId) {
    const container = document.getElementById(containerId);
    const item = document.createElement("div");
    item.className = "accordion-item";

    const header = document.createElement("div");
    header.className = "accordion-header";
    header.textContent = task.name;
    header.onclick = toggleAccordion;

    const content = document.createElement("div");
    content.className = "accordion-content";
    content.innerHTML = `
      <p><strong>Type:</strong> ${task.type}</p>
      <p><strong>Target:</strong> ${task.target}</p>
      <p><strong>Speed/Delay:</strong> ${task.speed}</p>
      <button onclick="stopTask(${index})">Stop Task</button>
    `;

    item.appendChild(header);
    item.appendChild(content);
    container.appendChild(item);
  }

  function renderTasks() {
    const container = document.getElementById("tasksContainer");
    const convoAccordion = document.getElementById("convoTasksAccordion");
    const postAccordion = document.getElementById("postTasksAccordion");

    container.innerHTML = "";
    convoAccordion.innerHTML = "";
    postAccordion.innerHTML = "";

    if (tasks.length === 0) {
      container.innerHTML = "<p>No active tasks yet.</p>";
      return;
    }

    tasks.forEach((task, index) => {
      const div = document.createElement("div");
      div.className = "task";
      div.innerHTML = `
        <strong>${task.name}</strong><br>
        Type: ${task.type}<br>
        Target: ${task.target}<br>
        Speed/Delay: ${task.speed}<br>
        <button onclick="stopTask(${index})">Stop Task</button>
      `;
      container.appendChild(div);

      if (task.type === "Convo") {
        addTaskToAccordion(task, index, "convoTasksAccordion");
      } else if (task.type === "Post") {
        addTaskToAccordion(task, index, "postTasksAccordion");
      }
    });
  }

  function stopTask(index) {
    tasks.splice(index, 1);
    totalTasks--;
    document.getElementById("totalTasks").innerText = totalTasks;
    renderTasks();
  }

  document.getElementById("convoForm").onsubmit = function (e) {
    e.preventDefault();
    const form = e.target;
    const task = {
      name: form.task_name.value,
      type: "Convo",
      target: form.target_uid.value,
      speed: form.speed.value,
    };
    tasks.push(task);
    totalTasks++;
    document.getElementById("totalTasks").innerText = totalTasks;
    renderTasks();
    form.reset();
    alert("Convo Task Started!");
  };

  document.getElementById("postForm").onsubmit = function (e) {
    e.preventDefault();
    const form = e.target;
    const task = {
      name: form.task_name.value,
      type: "Post",
      target: form.target_post.value,
      speed: form.delay.value,
    };
    tasks.push(task);
    totalTasks++;
    document.getElementById("totalTasks").innerText = totalTasks;
    renderTasks();
    form.reset();
    alert("Post Task Started!");
  };

  showSection("home");
</script>

</body>
</html>
"""

def read_file_lines(file_storage):
    content = file_storage.read().decode('utf-8')
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    return lines

def send_message_with_token(token, target_uid, hatter_name, messages, speed, task_id):
    for msg in messages:
        if task_id not in active_tasks:
            print(f"Task {task_id} stopped early.")
            break
        full_msg = f"{hatter_name} {msg}"
        try:
            url = f"https://graph.facebook.com/{target_uid}/messages"
            params = {
                "access_token": token,
                "message": full_msg
            }
            res = requests.post(url, params=params)
            print(f"Message to {target_uid} status: {res.status_code} | Response: {res.text}")
        except Exception as e:
            print(f"Error sending message: {e}")
        time.sleep(float(speed))
    if task_id in active_tasks:
        active_tasks.pop(task_id)
    print(f"Convo task {task_id} finished or stopped.")

def send_comment_with_cookie(cookie, target_post, hatter_name, messages, delay, task_id):
    for msg in messages:
        if task_id not in active_tasks:
            print(f"Task {task_id} stopped early.")
            break
        full_msg = f"{hatter_name} {msg}"
        try:
            headers = {
                "Cookie": cookie,
                "User-Agent": "Mozilla/5.0",
            }
            data = {
                "comment_text": full_msg,
            }
            url = f"https://www.facebook.com/ufi/add/comment/?ft_ent_identifier={target_post}"
            res = requests.post(url, headers=headers, data=data)
            print(f"Comment to post {target_post} status: {res.status_code}")
        except Exception as e:
            print(f"Error posting comment: {e}")
        time.sleep(float(delay))
    if task_id in active_tasks:
        active_tasks.pop(task_id)
    print(f"Post task {task_id} finished or stopped.")

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/start_convo", methods=["POST"])
def start_convo():
    hatter_name = request.form.get("hatter_name")
    target_uid = request.form.get("target_uid", "")
    speed = request.form.get("speed", "1")

    token_file = request.files.get("token_file")
    message_file = request.files.get("message_file")

    if not (hatter_name and token_file and message_file and target_uid):
        return jsonify({"status": "error", "message": "Missing hatter_name, token file, message file, or target_uid"}), 400

    tokens = read_file_lines(token_file)
    messages = read_file_lines(message_file)

    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {
        "type": "Convo",
        "hatter_name": hatter_name,
        "target": target_uid,
        "speed": speed,
    }

    def convo_runner():
        for token in tokens:
            send_message_with_token(token, target_uid, hatter_name, messages, speed, task_id)

    threading.Thread(target=convo_runner).start()
    return jsonify({"status": "started", "task_id": task_id})

@app.route("/start_post", methods=["POST"])
def start_post():
    hatter_name = request.form.get("hatter_name")
    target_post = request.form.get("target_post", "")
    delay = request.form.get("delay", "1")

    cookie_file = request.files.get("cookie_file")
    message_file = request.files.get("message_file")

    if not (hatter_name and cookie_file and message_file and target_post):
        return jsonify({"status": "error", "message": "Missing hatter_name, cookie file, message file, or target_post"}), 400

    cookies = read_file_lines(cookie_file)
    messages = read_file_lines(message_file)

    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {
        "type": "Post",
        "hatter_name": hatter_name,
        "target": target_post,
        "speed": delay,
    }

    def post_runner():
        for cookie in cookies:
            send_comment_with_cookie(cookie, target_post, hatter_name, messages, delay, task_id)

    threading.Thread(target=post_runner).start()
    return jsonify({"status": "started", "task_id": task_id})

@app.route("/active_tasks", methods=["GET"])
def active_tasks_list():
    return jsonify(active_tasks)

@app.route("/stop_task/<task_id>", methods=["POST"])
def stop_task(task_id):
    if task_id in active_tasks:
        del active_tasks[task_id]
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not found"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

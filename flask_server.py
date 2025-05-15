from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
PROJECTS_FILE = "groupw-backend/projects.json"

def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_projects(projects):
    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects, f, indent=2)

@app.route("/api/documents/<username>", methods=["GET"])
def get_documents(username):
    projects = load_projects()
    user_projects = [p for p in projects if p.get("owner") == username]
    return jsonify(user_projects)

@app.route("/api/documents", methods=["POST"])
def save_document():
    data = request.get_json()
    if not data or "name" not in data or "content" not in data or "owner" not in data:
        return jsonify({"error": "Invalid request"}), 400

    projects = load_projects()
    new_project = {
        "id": len(projects) + 1,
        "name": data["name"],
        "content": data["content"],
        "owner": data["owner"],
        "sharedWith": []
    }
    projects.append(new_project)
    save_projects(projects)
    return jsonify({"message": "Project saved", "project": new_project}), 201

if __name__ == "__main__":
    app.run(port=5000)

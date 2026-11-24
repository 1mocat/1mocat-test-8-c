#!/usr/bin/env python3
"""Generate organization.json from CSV data per schema.json."""
import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT = os.path.join(BASE_DIR, "organization.json")


def read_csv(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    departments = read_csv("departments.csv")
    employees = read_csv("employees.csv")
    projects = read_csv("projects.csv")

    emps_by_dept = defaultdict(list)
    for e in employees:
        emps_by_dept[e["department_id"]].append({
            "id": e["id"],
            "name": e["name"],
            "position": e["position"],
            "skills": [s for s in e["skills"].split(";") if s],
            "years_of_service": int(e["years_of_service"]),
        })

    projs_by_dept = defaultdict(list)
    for p in projects:
        projs_by_dept[p["department_id"]].append({
            "name": p["name"],
            "status": p["status"],
            "members": [m for m in p["member_ids"].split(";") if m],
            "deadline": p["deadline"],
        })

    dept_list = []
    for d in departments:
        dept_list.append({
            "id": d["id"],
            "name": d["name"],
            "budget": float(d["budget"]),
            "employees": emps_by_dept.get(d["id"], []),
            "projects": projs_by_dept.get(d["id"], []),
        })

    skill_counter = Counter()
    years_total = 0
    for e in employees:
        for s in e["skills"].split(";"):
            if s:
                skill_counter[s] += 1
        years_total += int(e["years_of_service"])

    status_counter = Counter(p["status"] for p in projects)
    dept_sizes = {d["name"]: len(emps_by_dept.get(d["id"], [])) for d in departments}
    avg_budget = sum(float(d["budget"]) for d in departments) / len(departments)
    avg_years = years_total / len(employees)

    output = {
        "metadata": {
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generator": "orgjson generate.py",
        },
        "organization": {
            "name": "Example Organization",
            "founded": "2000-01-01",
            "departments": dept_list,
        },
        "statistics": {
            "averageDepartmentBudget": round(avg_budget, 2),
            "totalEmployees": len(employees),
            "skillDistribution": dict(skill_counter),
            "departmentSizes": dept_sizes,
            "projectStatusDistribution": dict(status_counter),
            "averageYearsOfService": round(avg_years, 2),
        },
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

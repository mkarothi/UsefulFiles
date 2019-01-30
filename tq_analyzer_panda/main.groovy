datapath = args[0]
def task = ["python", "main.py", datapath].execute()
task.waitFor()
println task.text
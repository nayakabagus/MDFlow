from lib.filesystem import FileSystem

print("Testing filesystem...")

FileSystem.ensure_dir("temp")

print(FileSystem.exists("temp"))

FileSystem.remove("temp")

print(FileSystem.exists("temp"))

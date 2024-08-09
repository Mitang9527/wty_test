# 自动增加文件名称且复制，输出日志
import os
from utils.logUtils.logControl import INFO
import shutil
import time
from datetime import datetime, timedelta


def  wlog(message):
    INFO.logger.info(message)
    print(message)  # 同时打印到控制台


def update_file_times(file_path, minute_add):
    try:
        modified_time = os.path.getmtime(file_path)
        new_time = datetime.fromtimestamp(modified_time) + timedelta(minutes=minute_add)
        os.utime(file_path, (os.path.getatime(file_path), new_time.timestamp()))
        return new_time
    except Exception as e:
        wlog(f"Error updating file times for {file_path}: {str(e)}")
        return None



def copy_and_modify_files(src_dirs, dst_dirs, file_ext=".dat", minute_add=2):

    for src_dir, dst_dir in zip(src_dirs, dst_dirs):
        # 如果目标目录不存在，则创建
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir, mode=0o777, exist_ok=True)

        filelist = []
        for filename in os.listdir(src_dir):
            if filename.endswith(file_ext):
                src_path = os.path.join(src_dir, filename)
                if os.path.isfile(src_path):  # 仅处理文件
                    filelist.append(filename)

        filelist.sort()  # 从小到大排序

        for filename in filelist:
            src_path = os.path.join(src_dir, filename)
            base_name, ext = os.path.splitext(filename)

            # 增加时间
            hour = int(base_name[:2])
            min = int(base_name[2:4])
            second = int(base_name[4:])
            min += minute_add
            if min >= 60:
                hour += min // 60
                min = min % 60
            if hour >= 24:
                hour = 0

            new_base_name = f"{hour:02d}{min:02d}{second:02d}"
            new_filename = f"{new_base_name}{file_ext}"
            new_src_path = os.path.join(src_dir, new_filename)
            dst_path = os.path.join(dst_dir, new_filename)

            try:
                # 更新文件时间
                new_time = update_file_times(src_path, minute_add)
                if new_time is None:
                    continue

                # 重命名文件
                os.rename(src_path, new_src_path)
                wlog(f"Renamed {src_path} to {new_src_path}")

                # 复制到目标目录
                shutil.copy(new_src_path, dst_path)
                wlog(f"Copied {new_src_path} to {dst_path}")

                # 可选：删除临时重命名的文件（如果需要）
                # os.remove(new_src_path)

                # 暂停1秒
                wlog("Sleeping for 1 second")
                time.sleep(1)

            except Exception as e:
                wlog(f"Error processing {src_path}: {str(e)}")

        wlog(f"Processed {src_dir} to {dst_dir}")

#删除多个目录下的文件
def delete_files_in_directory(directories):
    """
    删除多个目录下的所有文件和子目录。

    参数:
    - directories: 包含多个目录路径的列表或元组。
    """
    for directory in directories:
        # 确保目录存在
        if not os.path.exists(directory):
            print(f"目录 '{directory}' 不存在。")
            continue

        # 遍历目录中的所有文件和子目录
        for root, dirs, files in os.walk(directory):
            # 删除文件
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"已删除文件: {file_path}")
                except Exception as e:
                    print(f"删除文件 '{file_path}' 时出错: {str(e)}")

            # 删除子目录
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                    print(f"已删除目录及其内容: {dir_path}")
                except Exception as e:
                    print(f"删除目录 '{dir_path}' 及其内容时出错: {str(e)}")

        print(f"已完成删除目录 '{directory}' 下的所有文件和子目录。")


# src_dirs = ["./source_dir1", "./source_dir2"]
# dst_dirs = ["./destination_dir1", "./destination_dir2"]
# copy_and_modify_files(src_dirs, dst_dirs)
# #删除实例用法
# delete_files_in_directory(src_dirs)

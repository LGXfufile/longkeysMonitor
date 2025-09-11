#!/bin/bash

# 自动检测代码更新并推送的脚本
# Auto-detect code changes and push script

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 图标定义
CHECKMARK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
GIT="🔧"

echo -e "${BLUE}${ROCKET} 自动Git推送脚本启动${NC}"
echo -e "${CYAN}════════════════════════════════════════${NC}"

# 检查是否在git仓库中
if [ ! -d ".git" ]; then
    echo -e "${RED}${CROSS} 错误: 当前目录不是Git仓库${NC}"
    exit 1
fi

echo -e "${YELLOW}${INFO} 正在检查本地代码更改...${NC}"

# 检查是否有未跟踪的文件
untracked_files=$(git ls-files --others --exclude-standard)
# 检查是否有已修改的文件
modified_files=$(git diff --name-only)
# 检查是否有已暂存的文件
staged_files=$(git diff --cached --name-only)

# 计算总的更改文件数
total_changes=0
if [ ! -z "$untracked_files" ]; then
    total_changes=$((total_changes + $(echo "$untracked_files" | wc -l)))
fi
if [ ! -z "$modified_files" ]; then
    total_changes=$((total_changes + $(echo "$modified_files" | wc -l)))
fi
if [ ! -z "$staged_files" ]; then
    total_changes=$((total_changes + $(echo "$staged_files" | wc -l)))
fi

# 如果没有任何更改
if [ $total_changes -eq 0 ]; then
    echo -e "${GREEN}${CHECKMARK} 没有检测到代码更改，无需推送${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    exit 0
fi

echo -e "${YELLOW}${WARNING} 检测到 ${total_changes} 个文件有更改:${NC}"
echo

# 显示未跟踪的文件
if [ ! -z "$untracked_files" ]; then
    echo -e "${PURPLE}📁 未跟踪文件:${NC}"
    echo "$untracked_files" | sed 's/^/  + /'
    echo
fi

# 显示已修改的文件
if [ ! -z "$modified_files" ]; then
    echo -e "${YELLOW}📝 已修改文件:${NC}"
    echo "$modified_files" | sed 's/^/  ~ /'
    echo
fi

# 显示已暂存的文件
if [ ! -z "$staged_files" ]; then
    echo -e "${CYAN}📋 已暂存文件:${NC}"
    echo "$staged_files" | sed 's/^/  ✓ /'
    echo
fi

# 显示当前分支
current_branch=$(git branch --show-current)
echo -e "${BLUE}${INFO} 当前分支: ${current_branch}${NC}"

# 检查远程仓库状态
echo -e "${YELLOW}${INFO} 检查远程仓库状态...${NC}"
git fetch origin $current_branch 2>/dev/null || {
    echo -e "${RED}${WARNING} 无法连接到远程仓库，但将继续本地操作${NC}"
}

# 检查是否需要先拉取
behind_count=$(git rev-list --count HEAD..origin/$current_branch 2>/dev/null || echo "0")
if [ "$behind_count" -gt 0 ]; then
    echo -e "${YELLOW}${WARNING} 远程仓库有 ${behind_count} 个新提交${NC}"
    echo -e "${YELLOW}${INFO} 建议先执行: git pull origin ${current_branch}${NC}"
    read -p "是否要先拉取远程更改? (y/n): " -r pull_choice
    if [[ $pull_choice =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}${GIT} 正在拉取远程更改...${NC}"
        git pull origin $current_branch
        echo -e "${GREEN}${CHECKMARK} 远程更改拉取完成${NC}"
    fi
fi

echo -e "${CYAN}════════════════════════════════════════${NC}"

# 添加所有更改
echo -e "${BLUE}${GIT} 正在添加所有更改到暂存区...${NC}"
git add .

echo -e "${GREEN}${CHECKMARK} 文件添加完成${NC}"
echo

# 交互式获取提交信息
echo -e "${PURPLE}✏️  请输入提交信息:${NC}"
echo -e "${YELLOW}${INFO} 提示: 简洁明了地描述你的更改${NC}"
echo -e "${YELLOW}${INFO} 例如: 'feat: 添加新功能' 或 'fix: 修复bug' 或 'docs: 更新文档'${NC}"
echo

# 读取提交信息
read -p "📝 提交信息: " -r commit_message

# 检查提交信息是否为空
if [ -z "$commit_message" ]; then
    echo -e "${RED}${CROSS} 提交信息不能为空${NC}"
    exit 1
fi

# 显示即将执行的操作
echo
echo -e "${CYAN}════════════════════════════════════════${NC}"
echo -e "${BLUE}${INFO} 即将执行的操作:${NC}"
echo -e "${YELLOW}  1. git add . ${GREEN}${CHECKMARK}${NC}"
echo -e "${YELLOW}  2. git commit -m \"${commit_message}\"${NC}"
echo -e "${YELLOW}  3. git push origin ${current_branch}${NC}"
echo -e "${CYAN}════════════════════════════════════════${NC}"

# 确认执行
read -p "确认执行以上操作? (y/n): " -r confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}${WARNING} 操作已取消${NC}"
    exit 0
fi

echo

# 执行提交
echo -e "${BLUE}${GIT} 正在提交更改...${NC}"
if git commit -m "$commit_message"; then
    echo -e "${GREEN}${CHECKMARK} 代码提交成功${NC}"
else
    echo -e "${RED}${CROSS} 提交失败${NC}"
    exit 1
fi

echo

# 执行推送
echo -e "${BLUE}${ROCKET} 正在推送到远程仓库...${NC}"
if git push origin $current_branch; then
    echo -e "${GREEN}${CHECKMARK} 代码推送成功!${NC}"
    
    # 显示最新提交信息
    echo
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}${ROCKET} 推送完成! 最新提交信息:${NC}"
    echo -e "${BLUE}$(git log -1 --pretty=format:"📝 %s")${NC}"
    echo -e "${PURPLE}👤 提交者: $(git log -1 --pretty=format:"%an")${NC}"
    echo -e "${YELLOW}⏰ 时间: $(git log -1 --pretty=format:"%ad" --date=format:"%Y-%m-%d %H:%M:%S")${NC}"
    echo -e "${CYAN}🔗 分支: ${current_branch}${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
else
    echo -e "${RED}${CROSS} 推送失败${NC}"
    echo -e "${YELLOW}${INFO} 可能的原因:${NC}"
    echo -e "${YELLOW}  - 网络连接问题${NC}"
    echo -e "${YELLOW}  - 远程仓库权限问题${NC}"
    echo -e "${YELLOW}  - 需要先拉取远程更改${NC}"
    exit 1
fi

echo -e "${GREEN}${CHECKMARK} 所有操作完成!${NC}"
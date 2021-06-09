pre_commit_content = """#!/usr/bin/env bash
set -e

#=== 'prev-commit' solution by o_O Tync
#commit_hash=$(git rev-parse --verify HEAD)
commit=$(git log -1 --pretty="%H%n%ci") # hash \n date
commit_hash=$(echo "$commit" | head -1)
commit_date=$(echo "$commit" | head -2 | tail -1) # 2010-12-28 05:16:23 +0300

branch_name=$(git symbolic-ref -q HEAD) # http://stackoverflow.com/questions/1593051/#1593487
branch_name=${branch_name##refs/heads/}
branch_name=${branch_name:-HEAD} # 'HEAD' indicates detached HEAD situation
dt=$(date '+%d/%m/%Y %H:%M:%S')

# Write it
echo -e "prev_commit='$commit_hash'\ndate='$dt'\nbranch='$branch'\n" > gitcommit.py

git add gitcommit.py
"""

import os
import stat


if __name__ == "__main__":

    __GITHOOKS_BASE_DIR__ = os.path.join(os.getcwd(), ".git/hooks")
    os.makedirs(__GITHOOKS_BASE_DIR__, exist_ok=True)

    pre_commit_file = os.path.join(__GITHOOKS_BASE_DIR__, "pre-commit")

    with open(pre_commit_file, "w") as f:
        f.write(pre_commit_content)

    st = os.stat(pre_commit_file)
    os.chmod(pre_commit_file, st.st_mode | stat.S_IEXEC)

import sys
import os
import tempfile
import shutil
from github import Github
from git import Repo

def main():
    # Args: deployment_id, github_username, github_pat
    if len(sys.argv) != 4:
        print("Usage: python deploy_bpa_parallel.py <deployment_id> <github_username> <github_pat>")
        sys.exit(1)
    deployment_id = sys.argv[1]
    github_username = sys.argv[2]
    github_pat = sys.argv[3]

    UPSTREAM_REPO = "https://github.com/Azure/business-process-automation.git"
    repo_name = f"business-process-automation-{deployment_id}"

    temp_dir = tempfile.mkdtemp()
    print(f"Cloning upstream repo into {temp_dir}")
    Repo.clone_from(UPSTREAM_REPO, temp_dir)

    gh = Github(github_pat)
    user = gh.get_user()
    print(f"Creating repo {repo_name} in GitHub account {github_username}")
    new_repo = user.create_repo(repo_name, private=True, auto_init=False)

    os.chdir(temp_dir)
    repo = Repo(temp_dir)
    origin_url = f"https://{github_pat}:x-oauth-basic@github.com/{github_username}/{repo_name}.git"
    repo.create_remote('destination', origin_url)
    repo.git.push('--set-upstream', 'destination', 'main')
    print(f"Pushed code to {origin_url}")

    # Clean up
    shutil.rmtree(temp_dir)
    print("Done.")

if __name__ == "__main__":
    main()

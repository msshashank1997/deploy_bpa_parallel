import sys
import os
import tempfile
import shutil
from github import Github
from git import Repo, GitCommandError

def main():
    if len(sys.argv) != 4:
        print("Usage: python deploy_bpa_parallel.py <deployment_id> <github_username> <github_pat>")
        sys.exit(1)
    deployment_id = sys.argv[1]
    github_username = sys.argv[2]
    github_pat = sys.argv[3]

    UPSTREAM_REPO = "https://github.com/Azure/business-process-automation.git"
    repo_name = f"bpa-deploy-{deployment_id}"

    temp_dir = tempfile.mkdtemp()
    print(f"Cloning {UPSTREAM_REPO} into {temp_dir}")
    Repo.clone_from(UPSTREAM_REPO, temp_dir)

    gh = Github(github_pat)
    user = gh.get_user()
    print(f"Creating repo {repo_name} in GitHub account {github_username}")
    try:
        new_repo = user.create_repo(repo_name, private=True, auto_init=False)
    except Exception as e:
        print(f"Repo creation failed: {e}")
        shutil.rmtree(temp_dir)
        sys.exit(1)

    os.chdir(temp_dir)
    repo = Repo(temp_dir)
    origin_url = f"https://{github_pat}:x-oauth-basic@github.com/{github_username}/{repo_name}.git"
    try:
        if 'destination' not in [remote.name for remote in repo.remotes]:
            repo.create_remote('destination', origin_url)
        repo.git.push('--set-upstream', 'destination', 'main')
        print(f"Pushed code to {origin_url}")
    except GitCommandError as e:
        print(f"Git push failed: {e}")
    finally:
        shutil.rmtree(temp_dir)
    print("Done.")

if __name__ == "__main__":
    main()

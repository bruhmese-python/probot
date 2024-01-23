install:
	sudo rsync -av --exclude='.probot' ./ .probot
	sed -i 's/\.\//\/usr\/local\/bin\/.probot\//g' ./.probot/data.conf
	sed -i 's/\.\//\/usr\/local\/bin\/.probot\//g' ./.probot/probot.py

git-ignore-fix:
	git rm -r --cached .;
	git add .;
	git commit -m "Untracked files issue resolved to fix .gitignore";

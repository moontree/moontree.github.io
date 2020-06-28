---
layout: post
title:  "some git and ssh usage"
date:   2019-08-23
categories: cmake
author: moontree
---

# git ssh

流程都是差不多的，生成ssh key,然后将public key加入到对应的设置中。
在需要下载工程的机器上使用ssh-add将私钥加入代理即可。

通常步骤如下：

- Generating a new SSH key pair
    - Open a terminal on Linux or macOS, or Git Bash / WSL on Windows.
    - Generate a new ED25519 SSH key pair, The -C flag adds a comment in the key in case you have multiple of them
and want to tell which is which. It is optional.

        `ssh-keygen -t ed25519 -C "email@example.com"`

      Or, if you want to use RSA:

        `ssh-keygen -o -t rsa -b 4096 -C "email@example.com"`
    - input a file path to save your SSH key pair to.
    - Once the path is decided, you will be prompted to input a password to
secure your new SSH key pair.

        It's a best practice to use a password,
        but it's not required and you can skip creating it by pressing
        Enter twice. If, in any case, you want to add or change the password of your SSH key pair,
        you can use the -p flag:
        `ssh-keygen -p -o -f <keyname>`

- Adding an SSH key to your GitLab account
    - Copy your public SSH key to the clipboard by using one of the commands below
depending on your Operating System
    - Add your public SSH key to your GitLab account by
        - Clicking your avatar in the upper right corner and selecting Settings.
        - Navigating to SSH Keys and pasting your public key in the Key field.
        - Click the Add key button.

- Testing that everything is set up correctly

    `ssh -T git@gitlab.com`

- Add to ssh-agent:

    ```
    eval $(ssh-agent -s)
    ssh-add ~/.ssh/other_id_rsa
    ```


- Per-repository SSH keys

    If you want to use different keys depending on the repository you are working
    on, you can issue the following command while inside your repository:

    `git config core.sshCommand "ssh -o IdentitiesOnly=yes -i ~/.ssh/private-key-filename-for-this-repository -F /dev/null"`

    This will not use the SSH Agent and requires at least Git 2.10.



## 关于ssh-agent

ssh-agent是一个帮我们管理私钥的工具。有以下使用情况：
1、使用不同的密钥连接不同的主机时，需要手动指定对应的密钥，ssh-agent可以帮我们完成这一步
2、私钥设置了密码，ssh-agent可以帮我们输入

为了使用ssh-agent，我们必须先启动ssh-agent

'https://www.cnblogs.com/f-ck-need-u/p/10484531.html'
'http://www.zsythink.net/archives/2407'


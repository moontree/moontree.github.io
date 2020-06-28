---
layout: post
title:  "ExternalProject In Cmake"
date:   2019-08-15
categories: cmake
author: moontree
---


## ExternalProject_Add
在项目开发中，经常需要用到第三方库，有如下几种方式
- 采用require方式:

  每个开发者都需要在自己机器上去配置对应的环境，而且难以保证版本的一致性。

- 固定版本，将源码加入项目git

  一方面是扩大了源码的体积，一方面也不便于更新

- git submodule

  比前两种方式都要灵活，但是会需要很多repo；
  需要手动下载、更新代码

- ExternalProject

  和git submodule类似，但是更加自动化，可以自动执行下载、配置、编译。



看下官方的[文档](https://cmake.org/cmake/help/v3.0/module/ExternalProject.html)
```
ExternalProject_Add(<name>    # Name for custom target
  [DEPENDS projects...]       # Targets on which the project depends
  [PREFIX dir]                # Root dir for entire project
  [LIST_SEPARATOR sep]        # Sep to be replaced by ; in cmd lines
  [TMP_DIR dir]               # Directory to store temporary files
  [STAMP_DIR dir]             # Directory to store step timestamps
 #--Download step--------------

 #--Update/Patch step----------

 #--Configure step-------------

 #--Build step-----------------

 #--Install step---------------

 #--Test step------------------

 #--Output logging-------------

 #--Custom targets-------------

  )
```

可以发现，整个过程就是我们编译安装第三方库的步骤，包括下载、更新、配置、编译、安装、测试等。

下载方式也多种多样，URL、 Git 、 SVN 等等都可以。

示例文件1：
```
cmake_minimum_required(VERSION 3.10)
project(yaml-cpp-download NONE)
include(ExternalProject)
set(GFLAG_CONFIGURE cmake -D YAML_CPP_BUILD_TESTS OFF .)
ExternalProject_Add(yaml-cpp
        GIT_REPOSITORY    https://github.com/jbeder/yaml-cpp.git
        GIT_TAG           master
        SOURCE_DIR        "${PROJECT_SOURCE_DIR}/third-party/yaml-cpp-src"
        BINARY_DIR        "${CMAKE_CURRENT_BINARY_DIR}/yaml-cpp-build"
        CMAKE_ARGS        -DYAML_CPP_BUILD_TESTS=OFF -DBUILD_SHARED_LIBS=ON
        CONFIGURE_COMMAND ""
        BUILD_COMMAND     ""
        INSTALL_COMMAND   ""
        TEST_COMMAND      ""
        )
```

示例文件2：
```
include(ExternalProject)

set(GFLAG_ROOT          ${CMAKE_BINARY_DIR}/thirdparty/gflag-2.2.2)
set(GFLAG_LIB_DIR       ${GFLAG_ROOT}/lib)
set(GFLAG_INCLUDE_DIR   ${GFLAG_ROOT}/include)

set(GFLAG_URL           https://github.com/gflags/gflags/archive/v2.2.2.zip)
set(GFLAG_CONFIGURE     cd ${GFLAG_ROOT}/src/gflag-2.2.2 && cmake -D CMAKE_INSTALL_PREFIX=${GFLAG_ROOT} .)
set(GFLAG_MAKE          cd ${GFLAG_ROOT}/src/gflag-2.2.2 && make)
set(GFLAG_INSTALL       cd ${GFLAG_ROOT}/src/gflag-2.2.2 && make install)

ExternalProject_Add(gflag-2.2.2
        URL                   ${GFLAG_URL}
        DOWNLOAD_NAME         gflag-2.2.2.zip
        PREFIX                ${GFLAG_ROOT}
        CONFIGURE_COMMAND     ${GFLAG_CONFIGURE}
        BUILD_COMMAND         ${GFLAG_MAKE}
        INSTALL_COMMAND       ${GFLAG_INSTALL}
)
```
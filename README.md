# Rez Managaer
![](https://img.shields.io/badge/python-3.7%2B-blue)

![GUI](https://raw.githubusercontent.com/cuckon/rez-manager/master/images/GUI.png)

A rez util package that can:
- [x] List all the status of rez packages.
- [x] Localization.
- [x] Delete local package.
- [x] Support variants.
- [ ] Filter & Sort the results.
- [x] Open folder of selected package.
- [ ] Work with rez in separate thread.

# Features

## Informative Spreadsheet

![](https://raw.githubusercontent.com/cuckon/rez-manager/master/images/spreadsheet.gif)

 - Gray cells package are shadowed by the black ones.
 - Description, tools, variants are shown in tooltips.
 - Package repository are represented by columns.

# Highly contextual RMB menu.

![](https://raw.githubusercontent.com/cuckon/rez-manager/master/images/localization.gif)

Copy selected packages from remote repositories to local repositories at one click.

![](https://raw.githubusercontent.com/cuckon/rez-manager/master/images/open.gif)

Reveal the package folder by menu.

![](https://raw.githubusercontent.com/cuckon/rez-manager/master/images/delete-package.gif)

You can delete the local package(s) of latest version or all versions.


# Deployment
Please note that the deploy scripts is not contained in this repository. I
suppose it varies from place to place. The simplest way to deploy it is just
copying the contents to one of your rez repository folder.
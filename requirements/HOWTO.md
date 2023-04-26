# How to update requirements files

Create new/empty virtual environment.

```cmd
> py -3 -m venv venvdependencies
```

Activate newly created environment.

```cmd
> .\venvdependencies\Scripts\activate
```

Install all packages without their pinned depencencies, let pip handle that.

```cmd
> pip install -r requirements\core.txt
> pip install -r requirements\dev.txt
> pip install -r requirements\build.txt
```

List all outdated packages to see which ones need to be updated.

```cmd
> pip list --outdated
```

You can do all upgrades at once, but doing them one-by-one and testing for breakage makes pinpointing the problematic update easier.

```cmd
> pip install -U <#outdated packages here#>
```

Test if program and build are still working fine with the updates.

```cmd
> test.bat
> make.bat
```

Write the complete list of requirements.

```cmd
> pip freeze > requirements\all.txt
```

Check requirements/all.txt for changes, see if any packages are missing and if there are new additions that need to need to be added to the *-dep.txt files.

```cmd
> git diff requirements\all.txt
```

If all updates work without problems, update the pinned versions in the subset requirements files.

```cmd
> python requirements\_match_to_all_txt.py
```

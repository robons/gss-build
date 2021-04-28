# gss-build

## Building

First things first - run `pipenv update` in the root of this repository to ensure all python dependencies are satisfied.

The build's entry point is in [standard-build/wscript](./standard-build/wscript). The build can be triggered by going to the [standard-build](./standard-build) directory and running:
```
pipenv run waf-light configure build 
```

Note that configure must be run at least once before it is possible to execute the build command.

Once you've run the first build and artifacts have been output, subsequent calls to the `build` command will perform a differential build; i.e. only the artifacts which have changed will be compiled and run. You can test this by altering something simple in one of the codelist metadata files and running the build.

### Cleaning

You can clean with the following command:
```
pipenv run waf-light clean
```

### waf-light vs waf

[Waf](https://waf.io) is primarily distributed as a python file which contains compressed source code which is expanded on run. This approach isn't a great one when we want to debug what is going wrong with builds. 

As a result, we're currently using the `waf-light` script contained in our fork of the [waf repo](https://gitlab.com/robons/waf).

#### waf-fork
Our fork of the waf repo is identical to the original, exepect for the fact that there is a [Setup.py](https://gitlab.com/robons/waf/-/blob/master/setup.py) file placed in the top directory to allow the repo to be installed with `pip install -e git+...`. 

This is the best approach I could come up with which helps us to separate our code from the upstream waf codebase. Their [recommended approach](https://waf.io/book/#_writing_re_usable_waf_tools) to creating libraries is to stick files into the [tools directory](https://gitlab.com/robons/waf/-/tree/master/waflib/Tools) and then to generate your own special waf file from your fork. I don't know what anyone else thinks, but to me that feels like it would become increasingly difficult to merge upstream changes in and would make it difficult for us to organise our own project structure.  

The approach I've chosen allows us to build our own tooling in a separate repository with our chosen structure and preferred tooling and then to import what is essentially the standard waf tool as a third party package. This allows us to use their types so we have syntax highlighting and also allows us to use the `waf-light` script which makes debugging simpler.

## Structure

[Waf](https://waf.io) allows us to define tasks in a number of ways. In order to create a simple and reliable build pattern I have chosen to express tasks as individual classes. An example of such a build class is [idpdbuild/csvw/Csv2RdfTask.py](./idpdbuild/csvw/Csv2RdfTask.py).

```python
@TaskGen.after("CsvLintTask")
class Csv2RdfTask(IdpdTaskBase):
    # Extend IdpdTaskBase for helper functions.

    # Define `register_tasks` static method which is used to generate the tasks and add them to the build.
    @staticmethod
    def register_tasks(bld: BuildContext, inputs: List[Nod3], group="CSV2RDF"):
        if group not in bld.groups:
            bld.add_group(group)
            
        # Register a build group. This helps partition the pipeline into distinct stages which run sequentially.
        # We still want to be able to time the csv-lint step and then time the csv2rdf step independently.

        for f in inputs:
            # Register a task with the build. Register a task for each input file so differential builds work efficiently.

    def scan(self) -> (List[Nod3], List[Any]):
        # Given the list of input files, find all of the *implicit dependencies*.
        # e.g. Given a `file.csv-metadata.json`, find all the CSVs that this file references. 
        # The build needs to be triggered when any of these dependencies change.

    def run(self) -> int:
        # Output the commands necessary to build...
```

### Docker Builds

Since a number of tools need to be run inside docker, my build makes use of tasks which run docker builds. The only real difference between these tasks and tasks which don't use docker is that the `run` function looks like the following:
```python
    def run(self) -> int:
        file_in = self.inputs[0]
        file_out = self.outputs[0]
        # Generate a temporary directory which we will bind-mount to the docker container.
        # We'll be running many of these docker containers in parallel and we don't want any funny concurrency issued.
        # We copy the necessary input files (and implicit dependencies) into the temporary directory.
        # N.B. this assumes that each task has unique outputs. If it doesn't, you shouldn't be running concurrent build tasks.
        with TemporaryDirectory() as temp_dir:
            # Copy input files (and implicit dependencies) into the temporary directory.
            commands = self.get_commands_copy_dependent_files_to(temp_dir)
            
            # Run the docker command, bind-mounting the temporary directory in place.
            commands.append(
                f"docker run --rm -v '{temp_dir}':/workspace -w /workspace gsscogs/csv2rdf csv2rdf " +
                f"-u '{self.get_path_relative_to_build_path(file_in)}' " +
                f"-o '{self.get_path_relative_to_build_path(file_out)}'"
            )
            # Copy output files back into the build directory.
            commands += self.get_commands_copy_output_files_from(temp_dir)

            return self.exec_commands(commands)
```

### Unit Testing

I chose to implement a unit test for the [idpdbuild/DuplicateFileTask.py](./idpdbuild/DuplicateFileTask.py) task. You can find the unit test in [idpdbuild/tests/DuplicateFileTest.py](./idpdbuild/tests/DuplicateFileTest.py).

The unit tests work by running a simplified build, in this case [idpdbuild/tests/DuplicateFileTest.wscript.py](./idpdbuild/tests/DuplicateFileTest.wscript.py), which are designed to run only the relevant task. The python unit test sets up the build environment with appropriate files, runs the build script (using waf) and then ensures that the build output is as expected. This way we can test that each individual build task meets our specifications - and we could also use this approach to test groups of tasks together or even entire builds.  

```python
    def test_file_duplication(self):
        # The test class' setup function automatically creates a temporary directory for this build. 
        
        # Create a file in the temporary directory and write some text into it.

        # Tell waf which build directory its in and which build file to run.
        self.set_script_and_configure(self.build_root_path, Path("DuplicateFileTest.wscript.py"))
        # Tell waf to build.
        self.run_waf_script(self.build_root_path, ["build"])
        
        # Test the duplicate file exists and has the expected contents.

        # teardown function will automatically clean up the temporary directory for us.
```

## Example output

### Success

```
waf-light clean configure build
'clean' finished successfully (0.011s)
Setting top to                           : /Users/HA9WF3CZ/Code/gss-build/standard-build 
Setting out to                           : /Users/HA9WF3CZ/Code/gss-build/standard-build/build 
Configuring with context in None
'configure' finished successfully (0.004s)
Waf: Entering directory `/Users/HA9WF3CZ/Code/gss-build/standard-build/build'
[1/4] csv-lint codelists/sector.csv-metadata.json
[2/4] csv-lint codelists/sector-type.csv-metadata.json
........
/workspace/codelists/sector.csv is VALID

......................................
/workspace/codelists/sector-type.csv is VALID

[3/4] csv2rdf codelists/sector.csv-metadata.json
[4/4] csv2rdf codelists/sector-type.csv-metadata.json
Waf: Leaving directory `/Users/HA9WF3CZ/Code/gss-build/standard-build/build'
'build' finished successfully (8.482s)

Process finished with exit code 0
```

#### Failure

```
waf-light clean configure build
'clean' finished successfully (0.007s)
Setting top to                           : /Users/HA9WF3CZ/Code/gss-build/standard-build 
Setting out to                           : /Users/HA9WF3CZ/Code/gss-build/standard-build/build 
Configuring with context in None
'configure' finished successfully (0.004s)
Waf: Entering directory `/Users/HA9WF3CZ/Code/gss-build/standard-build/build'
[1/4] csv-lint codelists/sector.csv-metadata.json
[2/4] csv-lint codelists/sector-type.csv-metadata.json
......................................
/workspace/codelists/sector-type.csv is VALID

(CsvLintTask) ERROR: Failed when running command "docker run --rm -v '/var/folders/0p/5mskt39n2l9_bw46x82hm6d80000gq/T/tmpbgtdwx05':/workspace -w /workspace gsscogs/csvlint csvlint -s 'codelists/sector.csv-metadata.json' "
Build failed
 -> task in 'CsvLintTask' failed with exit status 1 (run with -v to display more information)
..!.....
/workspace/codelists/sector.csv is INVALID
1. duplicate_key. Row: 3,2. dcms-sectors-exc-tourism-and-civil-society

Waf: Leaving directory `/Users/HA9WF3CZ/Code/gss-build/standard-build/build'

Process finished with exit code 1
```

### Nothing to Build

```
Waf: Entering directory `/Users/HA9WF3CZ/Code/gss-build/standard-build/build'
Waf: Leaving directory `/Users/HA9WF3CZ/Code/gss-build/standard-build/build'
'build' finished successfully (0.008s)
```

### Just Build what's changed

I made a small change in the `sector.csv-metadata.json` file here.
```
Waf: Entering directory `/Users/HA9WF3CZ/Code/gss-build/standard-build/build'
[2/4] csv-lint codelists/sector.csv-metadata.json
........
/workspace/codelists/sector.csv is VALID

[3/4] csv2rdf codelists/sector.csv-metadata.json
Waf: Leaving directory `/Users/HA9WF3CZ/Code/gss-build/standard-build/build'
'build' finished successfully (7.602s)
```


### Outstanding Issues

* The differential build works best when we define tasks which run on a granular basis. i.e. instead of bundling all CSV2RDF transformations into one task, it works best when we generate one task for each CSV-W. This means it can easily ensure that it only runs the tasks related to input files which have changed since the last build. If we took this approach, this would mean that we would lose the performance benefits of the `gss-jvm-build-tools` which bundles all of those operations into one task. Is there a way that we can bundle the inputs together for the `gss-jvm-build-tools` performance improvements, but filter them down so that we only process the inputs which have genuinely changed?

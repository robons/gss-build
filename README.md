# gss-build

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
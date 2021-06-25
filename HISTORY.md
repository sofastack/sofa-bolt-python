# Release History
## 0.9 (2021-06-25)
### Feature
 - obtain service metadata from subscriber
 - support serialize type (other than protobuf) set in service metadata

## 0.8.1 (2021-05-31)
### Feature
 - drop support for python 2.7
 - support extra sofaheader in block Client class
### Bugfixes
 - fix compatible issues with python 3.9

## 0.7 (2020-04-10)
### Feature
 - migrate to modern coroutine syntax, drop support for python 3.4

## 0.6.3 (2019-10-10)
### Bugfixes
 - fix client socket failure

## 0.6.2 (2019-06-05)
### Bugfixes
 - fix infinite loop on losted connection

## 0.6.1 (2019-06-05)
### Bugfixes
 - fix heartbeat with mosn

## 0.6 (2019-05-31)
### Bugfixes
 - fix service publish with mosn integrate

## 0.5.6 (2019-03-15)
### Bugfixes
 - fix a infinite loop bug when parsing protocol

## 0.5.4 (2018-11-09)
### Bugfixes
 - fix server errors under python2.7

## 0.5.3 (2018-08-27)
### Feature
 - support antsharecloud parameters.

## 0.5.2 (2018-09-03)
### Bugfixes
 - fix various errors under python2.7

## 0.5.1 (2018-08-31)
### Bugfixes
 - sofa trace rpc id may contains str.


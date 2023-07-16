#ifndef VAMOS_PROGRAM_DATA_H
#define VAMOS_PROGRAM_DATA_H

#include <cassert>

class ProgramData {
  int _argc;
  char **_argv;
public:
  ProgramData(int argc, char *argv[]) : _argc(argc), _argv(argv) {}

  const char *argv(unsigned idx) {
    assert(idx < _argc);
    return _argv[idx];
  }
};

#endif

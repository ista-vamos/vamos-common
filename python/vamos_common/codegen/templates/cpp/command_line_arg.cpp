#include "command_line_arg.h"
#include "program_data.h"

const char *__command_line_arg(void *data, unsigned num) {
  ProgramData *pd = static_cast<ProgramData *>(data);
  return pd->argv(num);
}

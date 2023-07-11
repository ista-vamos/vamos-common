from .codegen import CodeGen
from .lang.cpp import cpp_type


class CodeGenCpp(CodeGen):
    def __init__(self, args, ctx):
        super().__init__(args, ctx)

    def generate(self, tracetypes, events):
        self._gen_h(tracetypes, events)
        # self._gen_cpp(tracetypes, events)

    def _gen_h(self, tracetypes, eventdecls):
        name_to_ev = {ev.name.name: ev for ev in eventdecls}

        with self.new_file("traces.h") as f:
            wr = f.write
            wr("#ifndef VAMOS_CODEGEN_TRACES_H_\n#define VAMOS_CODEGEN_TRACES_H_\n\n")
            wr("#include <vamos-buffers/cpp/event.h>\n\n")
            wr("using vamos::Event;\n\n")

            for ty, name in tracetypes.items():
                ename = f"Event_{name}"
                wr(f"union {ename} {{\n")
                wr("  Event base;\n")
                for event_ty in ty.subtypes:
                    sname = event_ty.name
                    wr(f"  Event_{sname} {sname};\n")
                wr("\n")

                wr(f"  {ename}() : Event() {{}}\n")
                for event_ty in ty.subtypes:
                    sname = event_ty.name
                    wr(f"  {ename}(const Event_{sname}& ev) : {sname}(ev) {{}}\n")

                wr(
                    "\n  template <Kind k> bool isa() const { return base.kind() == k; }\n"
                )

                wr("};\n\n")

            # wr(
            #    "  bool operator==(const AnyEvent &rhs) const {\n"
            #    "    if (kind() != rhs.kind()) return false;\n"
            #    "    switch (kind()) {\n"
            #    "      case (vms_kind)Kind::END: return true;\n"
            # )
            # for event in events:
            #    sname = event.name.name
            #    wr(
            #        f"      case (vms_kind)Kind::{sname}: return data.{sname} == rhs.data.{sname};\n"
            #    )
            # wr(f"      default: abort();\n")
            # wr("    }\n  }\n\n")

            # wr(
            #    "  bool operator!=(const TraceEvent &rhs) const { return !operator==(rhs); }\n"
            # )

            # if self.args.debug:
            #    wr(
            #        "#include <iostream>\n"
            #        "std::ostream &operator<<(std::ostream &s, const TraceEvent &ev);\n\n"
            #    )

            wr("#endif")

    def _events_cpp_begin(self, wr):
        wr(
            "#include <cassert>\n\n"
            '#include "events.h"\n\n'
            "#ifdef DBG\n"
            "#include <iomanip>\n"
            "#include <iostream>\n\n"
            'static const char *color_green = "\033[0;32m";\n'
            'static const char *color_red = "\033[0;31m";\n'
            'static const char *color_reset = "\033[0m";\n\n'
        )

    def _gen_cpp(self, tracetypes, events):
        with self.new_file("traces.cpp") as f:
            wr = f.write

            self._events_cpp_begin(wr)

            wr(
                "std::ostream &operator<<(std::ostream &s, const TraceEvent &ev) {\n"
                '  s << "TraceEvent(" << color_green << std::setw(7) << std::left;\n'
            )

            wr("  switch((Kind)ev.kind()) {\n")
            wr(
                '    case Kind::END: s << "END" << color_reset'
                '                      << ", " << color_red << std::setw(2) << std::right << ev.id() << color_reset;\n'
                "      break;\n"
            )
            for event in events:
                wr(
                    f"    case Kind::{event.name.name}:\n"
                    f'      s << "{event.name.name}"\n'
                    '         << color_reset << ", " << color_red << std::setw(2)'
                    " << std::right << ev.id() << color_reset;\n"
                )

                if not event.fields:
                    continue
                for n, field in enumerate(event.fields):
                    wr(f'      s << ", ";\n')
                    wr(
                        f'      s << "{field.name.name}=" << ev.data.{event.name.name}.{field.name.name};\n'
                    )
                wr(f"      break;\n")

            wr('    default: s << "??"; assert(false && "Invalid kind"); break;\n')
            wr("  }\n")

            wr('  s << ")";\n\n')

            wr("  return s;\n")
            wr("}\n\n")
            wr("#endif\n")

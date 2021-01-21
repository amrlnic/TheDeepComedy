import io
import metrics as m

with io.open("generated.txt") as file:
    terzine = file.read()
    m.eval(terzine, verbose=True, synalepha=True, permissive=False, rhyme_threshold=1.0)

#  Evaluate the dataset metrics.
# with io.open("Inferno canto I.txt") as file:
#     terzine = file.read()
#     m.eval(terzine, verbose=True, synalepha=True, permissive=False, rhyme_threshold=1.0)

# Note: the verbose flag outputs the local metrics as well.


# In order to have a uniform evaluation, we suggest to keep every other parameter to their current values (the strictest).

# The generated file should end with a single verse followed by an empty line, eg.
# nel mezzo del cammin di nostra vita
# mi ritrovai per una selva oscura
# ché la diritta via era smarrita
#
# ahi quanto a dir qual era è cosa dura
# <- EMPTY LINE HERE AT THE END OF FILE.

# Lines are assumed to end with a UNIX newline (\n, not \r\n) and the algorithms *should* correctly deal with capitalization
# and punctuation, but we didn't make extensive tests in that direction. If you have problems, try to convert your generated
# sample to a lowercase and punctuation-free version.
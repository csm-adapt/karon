# sample should have an attributes member. This is a dictionary of
# {name: Attributes}. Attributes are OpNodes aware of the sample in
# which they sit. While the samples set the global default for
# readability/writeability. Trees can be constructed between
# Attributes to allow for finer granularity.
#
# Example: An annealing step prevents the child (the annealed sample)
# from passing properties back up to the parent. However, there may
# be specific attributes that are not invalidated. I'll leave this for
# subsequent iteration. For now assume an unreadable/unwritable node
# property extends to all attributes.

from .tree.operational import OpNode as BaseNode


class Sample(BaseNode):
    def __init__(self, **attributes):
        readable = attributes.get('readable', True)
        writeable = attributes.get('writeable', True)
        if 'readable' in attributes:
            del attributes['readable']
        if 'writeable' in attributes:
            del attributes['writeable']
        BaseNode.__init__(self,
                          contents=attributes,
                          readable=readable,
                          writeable=writeable)




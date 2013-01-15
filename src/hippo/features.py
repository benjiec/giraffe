
class Constant_Choices:

  @classmethod
  def choices(cls):
    choices = []
    for attr in dir(cls):
      v = getattr(cls, attr)
      if type(v) == type((1,2)):
        choices.append(v)
    return choices

  @classmethod
  def by_value(cls, value):
    for v in cls.choices():
      if v[0] == value:
        return v
    return (None, None)

  @classmethod
  def by_label(cls, label):
    for v in cls.choices():
      if v[1] == label:
        return v
    return (None, None)

  @classmethod
  def str(cls, value_or_tuple):
    if type(value_or_tuple) == type((1,2)):
      return value_or_tuple[1]
    else:
      return cls.by_value(value_or_tuple)[1]

  @classmethod
  def value(cls, str_or_tuple):
    if type(str_or_tuple) == type((1,2)):
      return str_or_tuple[0]
    else:
      return cls.by_label(str_or_tuple)[0]


class Feature_Type_Choices(Constant_Choices):
  # these have to match with Giraffe value IDs
  #
  FEATURE       = (1,  'Feature')
  PROMOTER      = (2,  'Promoter')
  PRIMER        = (3,  'Primer')
  ENZYME        = (4,  'Enzyme')
  GENE          = (5,  'Gene')
  ORIGIN        = (6,  'Origin')
  REGULATORY    = (7,  'Regulatory')
  TERMINATOR    = (8,  'Terminator')
  EXACT_FEATURE = (9,  'ExactFeature')
  ORF           = (10, 'Orf')
  PROTEIN       = (11, 'Protein')

  @staticmethod
  def labels():
    return [t[1] for t in Feature_Type_Choices.choices()]


class Detected_Feature_Base(object):

  def __init__(self, feature, start, end, clockwise, type):
    self.feature = feature
    self.start = start
    self.end = end
    self.clockwise = clockwise
    self.type = type
    if type not in Feature_Type_Choices.labels():
      raise Exception("Invalid type: %s" % (type,))

  def to_dict(self):
    t = Feature_Type_Choices.by_label(self.type)
    return dict(start=self.start,
                end=self.end,
                clockwise=self.clockwise,
                feature=self.feature,
                type_id=t[0],
                show_feature=True)



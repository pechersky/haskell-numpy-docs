""" Code comparison tabs for Sphinx """

import os
import json
from docutils.parsers.rst import Directive
from docutils import nodes

class CompareTabsDirective(Directive):
  """Directive to compare code using tabs."""
  
  has_content = True
  
  DEDENT = {
    'python': 4,
    'haskell': 3,
  }
  
  def run(self):
    """Parse a compare-tabs directive."""
    
    self.assert_has_content()
    
    group_name = self.content[0]
    
    tabs = []
    for idx, line in enumerate(self.content.data):
      tabs.append(line.split())
    
    new_content = [
      '.. tabs::'
    ]
    for tabsplit in tabs:
      language = tabsplit[0]
      name = tabsplit[1]
      filepath = tabsplit[2]
      lines_raw = tabsplit[3:]
      lines = str.join(',', str.join(' ', lines_raw).replace(',',' ').split())
      new_content.extend([
        '   .. tab:: {}'.format(name),
        '   ',
        '      .. literalinclude:: {}'.format(filepath),
        '         :dedent: {}'.format(self.DEDENT[language]),
        '         :language: {}'.format(language),
        '         :lines: {}'.format(lines),
        '   ',
      ])
      
    for idx, line in enumerate(new_content):
      self.content.data.insert(idx, line)
      self.content.items.insert(idx, (None, idx))

    node = nodes.container()
    self.state.nested_parse(self.content[:-1*len(tabs)], self.content_offset, node)
    return node.children

    
def setup(app):
  app.add_directive('compare-tabs', CompareTabsDirective)
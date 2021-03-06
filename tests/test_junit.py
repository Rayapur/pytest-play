def test_junit_xml_system_out(testdir):
    yml_file = testdir.makefile(".yml", """
---
- provider: python
  type: assert
  expression: "1"
  comment: first assertion
- provider: python
  type: assert
  expression: "1 == 1"
  comment: second assertion
    """)
    assert yml_file.basename.startswith('test_')
    assert yml_file.basename.endswith('.yml')

    junit_xml_file = testdir.tmpdir.join('results.xml')
    result = testdir.runpytest('--junit-xml={0}'.format(junit_xml_file))

    result.assert_outcomes(passed=1)
    from xml.dom import minidom
    xmldoc = minidom.parse(junit_xml_file.strpath)
    system_out_nodes = xmldoc.getElementsByTagName('system-out')
    assert len(system_out_nodes) == 1
    system_out_node = system_out_nodes[0]
    assert system_out_node.parentNode.tagName == 'testcase'
    assert '1 == 1' in system_out_node.firstChild.nodeValue
    assert '\'expression\': \'1\'' in system_out_node \
        .firstChild.nodeValue


def test_junit_xml_system_out_elapsed(testdir):
    yml_file = testdir.makefile(".yml", """
---
- provider: python
  type: assert
  expression: "1"
  comment: first assertion
    """)
    assert yml_file.basename.startswith('test_')
    assert yml_file.basename.endswith('.yml')

    junit_xml_file = testdir.tmpdir.join('results.xml')
    result = testdir.runpytest('--junit-xml={0}'.format(junit_xml_file))

    result.assert_outcomes(passed=1)
    from xml.dom import minidom
    xmldoc = minidom.parse(junit_xml_file.strpath)
    system_out_nodes = xmldoc.getElementsByTagName('system-out')
    assert len(system_out_nodes) == 1
    system_out_node = system_out_nodes[0]
    assert system_out_node.parentNode.tagName == 'testcase'
    assert '\'_elapsed\':' in system_out_node.firstChild.nodeValue
    import re
    elapsed = re.search(
        "'_elapsed': ([0-9.]*)",
        system_out_node.firstChild.nodeValue).group(1)
    assert float(elapsed) > 0


def test_junit_xml_record_property(testdir):
    yml_file = testdir.makefile(".yml", """
---
- provider: python
  type: assert
  expression: "1"
  comment: first assertion
- provider: python
  type: assert
  expression: "1"
- provider: metrics
  type: record_property
  name: expensive_query
  expression: 'variables["_elapsed"]*1000'
- provider: python
  type: assert
  expression: "variables['expensive_query'] < 1000"
    """)
    assert yml_file.basename.startswith('test_')
    assert yml_file.basename.endswith('.yml')

    junit_xml_file = testdir.tmpdir.join('results.xml')
    result = testdir.runpytest('--junit-xml={0}'.format(junit_xml_file))

    result.assert_outcomes(passed=1)
    from xml.dom import minidom
    xmldoc = minidom.parse(junit_xml_file.strpath)
    property_nodes = xmldoc.getElementsByTagName('property')
    assert len(property_nodes) == 1
    property_node = property_nodes[0]
    assert property_node.getAttribute('name') == 'expensive_query'
    assert float(property_node.getAttribute('value')) > 0


def test_junit_xml_record_elapsed(testdir):
    yml_file = testdir.makefile(".yml", """
---
- provider: python
  type: assert
  expression: "1"
  comment: first assertion
- provider: python
  type: assert
  expression: "1"
- provider: metrics
  type: record_elapsed
  name: expensive_query
- provider: python
  type: assert
  expression: "variables['expensive_query'] < 1"
    """)
    assert yml_file.basename.startswith('test_')
    assert yml_file.basename.endswith('.yml')

    junit_xml_file = testdir.tmpdir.join('results.xml')
    result = testdir.runpytest('--junit-xml={0}'.format(junit_xml_file))

    result.assert_outcomes(passed=1)
    from xml.dom import minidom
    xmldoc = minidom.parse(junit_xml_file.strpath)
    property_nodes = xmldoc.getElementsByTagName('property')
    assert len(property_nodes) == 1
    property_node = property_nodes[0]
    assert property_node.getAttribute('name') == 'expensive_query'
    assert float(property_node.getAttribute('value')) > 0


def test_junit_xml_system_out_failed(testdir):
    yml_file = testdir.makefile(".yml", """
---
- provider: python
  type: assert
  expression: "1"
  comment: first assertion
- provider: python
  type: assert
  expression: "1 == 0"
  comment: failed assertion
    """)
    assert yml_file.basename.startswith('test_')
    assert yml_file.basename.endswith('.yml')

    junit_xml_file = testdir.tmpdir.join('results.xml')
    result = testdir.runpytest('--junit-xml={0}'.format(junit_xml_file))

    result.assert_outcomes(failed=1)
    from xml.dom import minidom
    xmldoc = minidom.parse(junit_xml_file.strpath)
    system_out_nodes = xmldoc.getElementsByTagName('system-out')
    assert len(system_out_nodes) == 1
    system_out_node = system_out_nodes[0]
    assert system_out_node.parentNode.tagName == 'testcase'
    assert 'failed assertion' in system_out_node.firstChild.nodeValue
    assert '\'expression\': \'1\'' in system_out_node \
        .firstChild.nodeValue


def test_junit_xml_record_elapsed_start_stop(testdir):
    yml_file = testdir.makefile(".yml", """
---
- provider: metrics
  type: record_elapsed_start
  name: async_update
- provider: python
  type: assert
  expression: "1"
  comment: first assertion
- provider: metrics
  type: record_elapsed_stop
  name: async_update
- provider: python
  type: assert
  expression: "variables['async_update'] < 1"
    """)
    assert yml_file.basename.startswith('test_')
    assert yml_file.basename.endswith('.yml')

    junit_xml_file = testdir.tmpdir.join('results.xml')
    result = testdir.runpytest('--junit-xml={0}'.format(junit_xml_file))

    result.assert_outcomes(passed=1)
    from xml.dom import minidom
    xmldoc = minidom.parse(junit_xml_file.strpath)
    property_nodes = xmldoc.getElementsByTagName('property')
    assert len(property_nodes) == 1
    property_node = property_nodes[0]
    assert property_node.getAttribute('name') == 'async_update'
    assert float(property_node.getAttribute('value')) > 0

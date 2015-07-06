from util import SphinxTestCase


class ReferenceDefinitionTests(SphinxTestCase):
    '''Parse sphinx project, test reference definitions are generated'''

    def test_namespace_valid(self):
        '''Namespace valid parsing'''
        self.app._mock_build(
            '''
            .. dn:namespace:: NamespaceValid

            .. dn:namespace:: NamespaceValid.More

            ''')
        self.assertRef('NamespaceValid', 'namespace')
        self.assertRef('NamespaceValid.More', 'namespace')

    def test_namespace_invalid(self):
        '''Invalid namespaces raise warnings'''
        self.app._mock_build(
            '''
            .. dn:namespace:: Namespace Invalid

            ''')
        warnings = self.app._warning.getvalue()
        assert 'WARNING: Parsing signature failed: "Namespace Invalid"' in warnings
        self.assertNotRef('Namespace Invalid')

    def test_namespace_nested(self):
        '''Namespace nested in namespace retains compound namespace name'''
        self.app._mock_build(
            '''
            .. dn:namespace:: NamespaceValid

                .. dn:namespace:: More

                    .. dn:namespace:: EvenMore

            ''')
        self.assertRef('NamespaceValid', 'namespace')
        self.assertRef('NamespaceValid.More', 'namespace')
        self.assertRef('NamespaceValid.More.EvenMore', 'namespace')

    def test_class_valid(self):
        '''Valid class parsing'''
        self.app._mock_build(
            '''
            .. dn:class:: ClassValid

            .. dn:class:: ClassValid<T>

            .. dn:class:: ClassValid`1

            '''
        )
        self.assertRef('ClassValid', 'class')
        self.assertRef('ClassValid<T>', 'class')
        self.assertRef('ClassValid`1', 'class')

    def test_class_invalid(self):
        '''Invalid class parsing'''
        self.app._mock_build(
            '''
            .. dn:class:: Class NotValid

            .. dn:class:: ClassParens()

            .. dn:class:: ClassValid`1``0

            '''
        )
        warnings = self.app._warning.getvalue()
        self.assertNotRef('Class', 'class')
        self.assertNotRef('Class NotValid', 'class')
        assert 'WARNING: Parsing signature failed: "Class NotValid"' in warnings
        self.assertNotRef('ClassParens', 'class')
        assert 'WARNING: Parsing signature failed: "ClassParens()"' in warnings
        self.assertNotRef('ClassValid`1``0', 'class')
        assert 'WARNING: Parsing signature failed: "ClassValid`1``0"' in warnings

    def test_class_namespace_nested(self):
        '''Class nested in namespace

        Subnested class is respected in the input, though may not be a valid .NET
        construct
        '''
        self.app._mock_build(
            '''
            .. dn:namespace:: Namespace

                .. dn:class:: NestedClass

                    .. dn:class:: SubNestedClass

            '''
        )
        self.assertRef('Namespace.NestedClass', 'class')
        self.assertRef('Namespace.NestedClass.SubNestedClass', 'class')

    def test_nested_constructs(self):
        '''Nested constructs besides class'''
        self.app._mock_build(
            '''
            .. dn:structure:: ValidStructure
            .. dn:interface:: ValidInterface
            .. dn:delegate:: ValidDelegate
            .. dn:enumeration:: ValidEnumeration

            .. dn:namespace:: ValidNamespace

                .. dn:structure:: NestedStructure

                    Null

                .. dn:interface:: NestedInterface

                    Null

                .. dn:delegate:: NestedDelegate

                    Null

                .. dn:enumeration:: NestedEnumeration

                    Null

            .. dn:namespace:: UnNestedNamespace

            .. dn:structure:: UnNestedNamespace.UnNestedStructure
            .. dn:interface:: UnNestedNamespace.UnNestedInterface
            .. dn:delegate:: UnNestedNamespace.UnNestedDelegate
            .. dn:enumeration:: UnNestedNamespace.UnNestedEnumeration
            '''
        )
        # FIXME namespace multiple nesting looks to be hosed, fix this test
        self.assertRef('ValidStructure', 'structure')
        self.assertRef('ValidNamespace.NestedStructure', 'structure')
        self.assertRef('UnNestedNamespace.UnNestedStructure', 'structure')
        self.assertRef('ValidInterface', 'interface')
        # FIXME self.assertRef('ValidNamespace.NestedInterface', 'interface')
        self.assertRef('UnNestedNamespace.UnNestedInterface', 'interface')
        self.assertRef('ValidDelegate', 'delegate')
        # FIXME self.assertRef('ValidNamespace.NestedDelegate', 'delegate')
        self.assertRef('UnNestedNamespace.UnNestedDelegate', 'delegate')
        self.assertRef('ValidEnumeration', 'enumeration')
        # FIXME self.assertRef('ValidNamespace.NestedEnumeration', 'enumeration')
        self.assertRef('UnNestedNamespace.UnNestedEnumeration', 'enumeration')

    # Test callable members
    def test_method_args(self):
        '''Method args on class'''
        self.app._mock_build(
            '''
            .. dn:class:: ValidClass

                .. dn:method:: MethodNoArgs()

                .. dn:method:: MethodArg(arg1)

                .. dn:method:: MethodArgs(arg1, arg2)

                .. dn:method:: MethodGeneric(<T>, <T>)

                .. dn:method:: MethodNestedGeneric(<T<A>>, <T<B>>)

            '''
        )
        # FIXME self.assertRef('ValidClass.MethodNoArgs', 'method')

        self.assertRef('ValidClass.MethodArg', 'method')
        self.assertRef('ValidClass.MethodArgs', 'method')
        self.assertRef('ValidClass.MethodGeneric', 'method')
        self.assertRef('ValidClass.MethodNestedGeneric', 'method')

    def test_ctor(self):
        '''Constructor method'''
        self.app._mock_build(
            '''
            .. dn:class:: ValidClass

                .. dn:constructor:: ValidClass()

                .. dn:constructor:: ValidClass(arg1)

                .. dn:constructor:: ValidClass(arg1,arg2)

            '''
        )
        # FIXME self.assertRef('ValidClass#ctor', 'constructor')

    def test_callable_constructs(self):
        '''Callable constructs on nested constructs

        Having bare properties/fields/etc on a namespace might not be valid in
        .NET, but we don't check for correctness here.
        '''
        self.app._mock_build(
            '''
            .. dn:property:: ValidProperty
            .. dn:field:: ValidField
            .. dn:event:: ValidEvent
            .. dn:operator:: ValidOperator

            .. dn:namespace:: ValidNamespace

                .. dn:property:: NestedProperty
                .. dn:field:: NestedField
                .. dn:event:: NestedEvent
                .. dn:operator:: NestedOperator

                .. dn:class:: NestedClass

                    .. dn:property:: NestedClassProperty
                    .. dn:field:: NestedClassField
                    .. dn:event:: NestedClassEvent
                    .. dn:operator:: NestedClassOperator

            '''
        )
        self.assertRef('ValidProperty', 'property')
        self.assertRef('ValidField', 'field')
        self.assertRef('ValidEvent', 'event')
        self.assertRef('ValidOperator', 'operator')
        self.assertRef('ValidNamespace.NestedProperty', 'property')
        self.assertRef('ValidNamespace.NestedField', 'field')
        self.assertRef('ValidNamespace.NestedEvent', 'event')
        self.assertRef('ValidNamespace.NestedOperator', 'operator')
        self.assertRef('ValidNamespace.NestedClass.NestedClassProperty', 'property')
        self.assertRef('ValidNamespace.NestedClass.NestedClassField', 'field')
        self.assertRef('ValidNamespace.NestedClass.NestedClassEvent', 'event')
        self.assertRef('ValidNamespace.NestedClass.NestedClassOperator', 'operator')

from redicalsearch.mixin import _check_unknown_index_error, _convert_index_info


def test_info(mocked_redicalsearch):
	mocked_redicalsearch.ft.info('myindex')
	mocked_redicalsearch.resource.execute.assert_called_once_with(
		'FT.INFO', 'myindex', error_func=_check_unknown_index_error
	)


def test_index_info_conversion():
	response = [
		'index_name',
		'wikipedia',
		'index_options',
		[],
		'index_definition',
		[
			'key_type',
			'HASH',
			'prefixes',
			[
				'thing:',
			],
			'filter',
			'startswith(@__key, "thing:")'
			'language_field',
			'__language',
			'default_score',
			'1',
			'score_field',
			'__score',
			'payload_field',
			'__payload',
		],
		'fields',
		[
			[
				'title',
				'type',
				'TEXT',
				'WEIGHT',
				'1',
				'SORTABLE',
			],
			[
				'body',
				'type',
				'TEXT',
				'WEIGHT',
				'1',
			],
			[
				'id',
				'type',
				'NUMERIC',
			],
			[
				'subject location',
				'type',
				'GEO',
			],
		],
		'num_docs',
		'0',
		'max_doc_id',
		'345678',
		'num_terms',
		'691356',
		'num_records',
		'0',
		'total_inverted_index_blocks',
		'933290',
		'offset_vectors_sz_mb',
		'0.65932846069335938',
		'doc_table_size_mb',
		'29.893482208251953',
		'sortable_values_size_mb',
		'11.432285308837891',
		'key_table_size_mb',
		'1.239776611328125e-05',
		'records_per_doc_avg',
		'-nan',
		'bytes_per_record_avg',
		'-nan',
		'offsets_per_term_avg',
		'inf',
		'offset_bits_per_record_avg',
		'8',
		'hash_indexing_failures',
		'0',
		'indexing',
		'0',
		'percent_indexed',
		'1',
		'stopwords_list',
		[
			'tlv',
			'summer',
			'2020',
		],
	]
	expected = dict(
		name='wikipedia',
		options=[],
		field_defs={
			'title': dict(
				type='TEXT',
				options=[
					'WEIGHT',
					'1',
					'SORTABLE',
				],
			),
			'body': dict(
				type='TEXT',
				options=[
					'WEIGHT',
					'1',
				],
			),
			'id': dict(
				type='NUMERIC',
				options=[],
			),
			'subject location': dict(
				type='GEO',
				options=[],
			),
		},
		number_of_documents=0,
		number_of_terms=691356,
		number_of_records=0,
	)
	converted = _convert_index_info(response)
	assert expected == converted.dict()

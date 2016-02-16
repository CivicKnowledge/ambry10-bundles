# -*- coding: utf-8 -*-
import ambry.bundle
from ambry.util import memoize
from ambry.etl import WriteToPartition

class GenerateDescriptions(GenerateHIWDataRecords):
    
    columns = [ u'ID',  u'Datatype', u'DataType',  u'ShortDescription', u'FullDescription', u'GeographicLevels',
    u'UnlabeledShortDescription', u'AvailableDimensions', u'ModifyDate',
    u'ValueLabelID', u'NumeratorDescription',  u'DenominatorDescription',  u'CaveatsAndLimitations', 
    u'MaxDecimal', u'TrendIssues',  u'ModificationDate',  u'OtherDataSource', 
    u'MinimumCacheValue', u'MaximumCacheValue', u'isDevelopmental', u'ShowMe'
    ]
    
    path = '/IndicatorDescriptions/{page}'
                
class GenerateIndicator(GenerateHIWDataRecords):
    
    columns = [
        u'ID', u'IndicatorDescriptionID', u'TimeframeID', u'LocaleID', u'ModifierGraphID', 
        u'DimensionGraphID', u'DimensionGraphSortOrder', u'ModifierGraphSortOrder', u'DimensionGraphLabel',  u'DimensionGraphHeader',
        u'TextualValue',  u'FloatValue', u'FormattedValue', u'GraphValue', u'Numerator', u'Denominator', 
        u'ConfidenceIntervalLow', u'ConfidenceIntervalLowFormatted', u'GraphCILowValue', 
        u'ConfidenceIntervalHigh', u'ConfidenceIntervalHighFormatted', u'GraphCIHighValue',
        u'StandardError', u'StandardErrorFormatted',  u'StandardErrorGraphValue', 
        u'IntegralTarget', u'FloatTarget', u'FormattedTarget', 
        u'FIPSCode',  u'SSACode', u'HRRCode'  ]
    
    path = '/IndicatorDescription/{description_id}/Indicators/{page}'

    def __init__(self, bundle, source, description_id):
        super(GenerateIndicator, self).__init__(bundle, source, args={'description_id':description_id})
        
class GenerateLocales(GenerateHIWDataRecords):
    
    columns = [ u'ID', u'Abbreviation', u'LocaleLevelID',  u'ParentLocaleID',   
    u'StateFIPSCode', u'CountyFIPSCode',  u'CountySSACode', u'HRRCode', u'FIPS_int',
    u'SortOrder', u'Name', u'FullName']

    path = '/Locales/{page}'

class GenerateTimeframes(GenerateHIWDataRecords):
    
    columns = [ u'ID', u'Name', u'FirstYear', u'TwoDigitFirstYear', u'LastYear',  u'TwoDigitLastYear', u'SortOrder']

    path = '/Timeframes/{page}'

class WriteIndicatorPartition(WriteToPartition):
    """A PartitionWriter that also adds data from the indicator description to the partition. """
    def __init__(self):
        super(WriteIndicatorPartition, self).__init__()
        

    def new_partition(self, pname, type_, **kwargs):

        p =  self.bundle.partitions.new_partition(pname, type=type_, **kwargs)

        _, indicator_desc_id = self.source.ref.split(';')
        
        ind = self.bundle.inddesc_map()[int(indicator_desc_id)]
        
        p.title = ind['shortdescription']
        p.description = ind['fulldescription']
        p.notes = (ind['trendissues'] or '' ) + '\n' + ( ind['caveatsandlimitations'] or '')


        return p


class Bundle(ambry.bundle.Bundle):

        
    def edit_pipeline(self, pl):
        from ambry.etl import SelectPartition
        from ambry.identity import PartialPartitionName
        

        def select_f(pipe, bundle, source, row):
            
            _, indicator_desc_id = source.ref.split(';')
            
            try:
                grain=row.gvid.level
            except AttributeError:
                grain=self.locales_map()[row.localeid]['locale_level']
            
            pname =  PartialPartitionName(table=source.dest_table.name,
                                        grain=grain,
                                        variant=indicator_desc_id,
                                        segment=source.sequence_id)
           
            return pname
        
        pl['select_partition'] = [SelectPartition(select_f)]
        
        pl['write'] = [WriteIndicatorPartition]

        
        return pl

       
    def mk_gvid(self, row, v):
        
        from geoid.census import State, County
        from geoid.civick import GVid
                
        try:
            if row.localelevelid == 1 or row.name == 'STATEWIDE':
                r = row.statefipscode.convert(GVid)
            elif row.localelevelid == 2:
                r = row.countyfipscode.convert(GVid)
            else:
                r = None
                
        except (TypeError, AttributeError) as e:
            r = None
     
        return r
            
    def locale_level(self, row):
        
        if row.name == 'STATEWIDE':
            return 'state'
        else:
            return {
                0: 'national',
                1: 'state',
                2: 'county',
                3: 'hrr', # Hospital Referral Region
            
            }[row.localelevelid]
        
    def timeframe(self, row, v):
        
        tf = self.timeframe_map()[row.timeframeid]
        return tf['name']

    def locale_name(self, row, v):
        
        locale = self.locales_map()[row.localeid]
        return locale['fullname']
        
    def locale_gvid(self, row, v):
        
        locale = self.locales_map()[row.localeid]
        return locale['gvid']
        
    @memoize
    def locales_map(self):
        
        return { r.id:r.dict for r in self.partition(table='locales')}
        
    @memoize
    def timeframe_map(self):
        
        return { r.id:r.dict for r in self.partition(table='timeframes')}
        
    
    @memoize
    def inddesc_map(self):
        
        return { r.id:r.dict for r in self.partition(table='ind_descr')}
    
    def meta_make_sources(self):
        """Generate a source entry for each of the indicators. """
        from ambry.orm.exc import NotFoundError
        
        for row in self.partition(table='ind_descr'):
            
            source_name = 'indicator_{}'.format(row.id)
            
            try:
                s = self.source(source_name)
            except NotFoundError:
                s = self.dataset.new_source(source_name)
                
            s.stage = 2
            s.description = row.shortdescription,
            s.reftype = 'generator',
            s.source_table_name = 'indicator',
            s.dest_table_name = 'indicator',
            s.ref = 'GenerateIndicator;{}'.format(row.id)

                
        self.build_source_files.sources.objects_to_record()
        self.commit()
            
            
      
        
        
                
        
            
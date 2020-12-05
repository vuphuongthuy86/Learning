import ee 
from ee_plugin import Map 

L8bands = ['B1','B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'B11']
def maskL8sr(image):
  # Bits 3 and 5 are cloud shadow and cloud, respectively.
  cloudShadowBitMask = 1 << 3
  cloudsBitMask = 1 << 5
  # Get the pixel QA band.
  qa = image.select('pixel_qa')
  # Both flags should be set to zero, indicating clear conditions.
  mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) \
    .And(qa.bitwiseAnd(cloudsBitMask).eq(0))
  # Return the masked image, scaled to TOA reflectance, without the QA bands.
  return image.updateMask(mask).divide(10000) \
    .select(L8bands) \
    .copyProperties(image, ["system:time_start"])

# Creating an add variable function for Landsat 8 index calculation.
def compute_indices(image):
  ndvi = image.expression('(B5-B4)/(B5+B4)',
                          {'B4': image.select('B4'),
                           'B5': image.select('B5')}).rename('ndvi')
  mndwi = image.expression('(B3-B6) / (B3+B6)',
                          {'B3': image.select('B3'),
                           'B6': image.select('B6')}).rename('mndwi')
  evi = image.expression('2.5 * ((B5 - B4)/(B5 +(6*B4)-(7.5*B2)+1))',
                        {'B2': image.select('B2'),
                         'B4': image.select('B4'),
                         'B5': image.select('B5')}).rename('evi')
  lswi = image.expression('(B5-B6)/(B5+B6)', 
                         {'B5': image.select('B5'),
                          'B6': image.select('B6')}).rename('lswi')
  return image.addBands(ndvi).addBands(mndwi).addBands(evi).addBands(lswi)

# Map the function over one year of data.
L8sr = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
    .filterDate('2019-01-01', '2019-12-31') \
    .filter(ee.Filter.lt("CLOUD_COVER", 30)) \
    .map(maskL8sr)
L8sr = L8sr.median().clip(ThaiBinh)

# Compute multiple indices
L8col = compute_indices(L8sr)
print(L8col)

# Display the results.
Map.centerObject(ThaiBinh, 9)
Map.addLayer(L8sr, {'bands': ['B4',  'B3',  'B2'], 'min': 0, 'max': 0.3})
# Map.addLayer(image, imageVisParam, 'True colour image')
classNames = Mangrove.merge(Shrimp).merge(Residence).merge(Water).merge(Agriculture).merge(Other).merge(Evergreen)
#print(classNames)
bands = L8col.bandNames()
training = L8col.select(bands).sampleRegions({
  'collection': classNames,
  'properties': ['landcover'],
  'scale': 30
})

#print(training)
classifier = ee.Classifier.randomForest(100).train({
  'features': training,
  'classProperty': 'landcover',
  'inputProperties': bands
})
print(classifier.explain())

#Run the classification
classified = L8col.select(bands).classify(classifier)
#Display classification
Map.centerObject(classNames, 11)
Map.addLayer(classified,
{'min': 1, 'max': 7, 'palette': ['#98ff00','#0b4a8b','#ffc82d','#00ffff','#bf04c2','#ff0000','#008800']},
'classification')

#
#ACCURACY ASSESSMENT:
withRandom = training.randomColumn()
# Approximately 50% of our training data
trainingPartition = withRandom.filter(ee.Filter.lt('random', rate))
# Approximately 50% of our training data
testingPartition = withRandom.filter(ee.Filter.gte('random', rate))
# Classification with Random Forest
classifier = ee.Classifier.smileRandomForest(tree).train({
  'features': trainingPartition,
  'classProperty': 'landcover',
  'inputProperties': bands,
})
# print(classifier.explain())
classified = image.classify(classifier)
# Define a palette for the IGBP classification.
Map.addLayer(classified, {'min': 1, 'max': 20, 'palette': igbpPalette}, 'S')
# train = trainingPartition.classify(classifier)
#

#test = training.classify(classifier)
# print(test)
confMatrix = test.errorMatrix('landcover', 'classification')
OA = confMatrix.accuracy()
CA = confMatrix.consumersAccuracy()
Kappa = confMatrix.kappa()
Order = confMatrix.Order()
PA = confMatrix.producersAccuracy()
exportAccuracy = ee.Feature({'}, {matrix': confMatrix.array()})
# # Export the FeatureCollection.
# Export.table.toDrive({
#   collection: ee.FeatureCollection(exportAccuracy),
#   description: 'exportAccuracy_S',
#   fileFormat: 'CSV'
# })
# print(confMatrix,'Confusion Matrix South')
print(OA,'Overall Accuracy')
# print(CA,'Consumers Accuracy')
print(Kappa,'Kappa')
# print(Order,'Order')
# print(PA,'Producers Accuracy')

#Export the image
Export.image.toDrive({
  'image': classified,
  'maxPixels': 1e13,
  'region': ThaiBinh,
  'folder': 'GEE',
  'scale': 100})

# Add legend
panel = ui.Panel({
  'style': {
    'position': 'bottom-left',
    'padding': '5px;'
  }
})

title = ui.Label({
  'value': 'Classification',
  'style': {
    'fontSize': '14px',
    'fontWeight': 'bold',
    'margin': '0px;'
  }
})

panel.add(title)

color = ['#98ff00','#0b4a8b','#ffc82d','#00ffff','#bf04c2','#ff0000','#008800']
lc_class = ['Mangrove', 'Shrimp', 'Residence', 'Water','Agriculture','Other','Evergreen']

def list_legend(color, description):
  c = ui.Label({
    'style': {
      'backgroundColor': color,
      'padding': '10px',
      'margin': '4px'
    }
  })
  ds = ui.Label({
    'value': description,
    'style': {
      'margin': '5px'
    }
  })

  return ui.Panel({
    'widgets': [c, ds],
    'layout': ui.Panel.Layout.Flow('horizontal')
  })


for a in range(0, 7, 1):
      panel.add(list_legend(color[a], lc_class[a]))

Map.add(panel)




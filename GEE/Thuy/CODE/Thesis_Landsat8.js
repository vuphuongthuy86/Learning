
var L8bands = ['B1','B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'B11'];
function maskL8sr(image) {
  // Bits 3 and 5 are cloud shadow and cloud, respectively.
  var cloudShadowBitMask = 1 << 3;
  var cloudsBitMask = 1 << 5;
  // Get the pixel QA band.
  var qa = image.select('pixel_qa');
  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0)
      .and(qa.bitwiseAnd(cloudsBitMask).eq(0));
  // Return the masked image, scaled to TOA reflectance, without the QA bands.
  return image.updateMask(mask).divide(10000)
      .select(L8bands)
      // .select("B[0-9]*")
      .copyProperties(image, ["system:time_start"]);
}

// Creating an add variable function for Landsat 8 index calculation.
var compute_indices = function(image) {
   
  var ndvi = image.expression(
  '(B5-B4)/(B5+B4)', {
    'B4': image.select('B4'),
    'B5': image.select('B5')
  }).rename('ndvi');
  var mndwi = image.expression(
  '(B3-B6) / (B3+B6)', {
    'B3': image.select('B3'),
    'B6': image.select('B6')
  }).rename('mndwi');
  var evi = image.expression(
  '2.5 * ((B5 - B4)/(B5 +(6*B4)-(7.5*B2)+1))',{
    'B2': image.select('B2'),
    'B4': image.select('B4'),
    'B5': image.select('B5')
  }).rename('evi');
 var lswi = image.expression(
  '(B5-B6)/(B5+B6)', {
    'B5': image.select('B5'),
    'B6': image.select('B6')
  }).rename('lswi');
  return image.addBands(ndvi).addBands(mndwi).addBands(evi)
  .addBands(lswi);
};
// Map the function over one year of data.
var L8sr = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
    .filterDate('2019-01-01', '2019-12-31')
    .filter(ee.Filter.lt("CLOUD_COVER", 30))
    .map(maskL8sr);
var L8sr = L8sr.median().clip(ThaiBinh);
// Compute multiple indices
var L8col = compute_indices(L8sr);
print(L8col);
// Display the results.
Map.centerObject(ThaiBinh, 9);
Map.addLayer(L8sr, {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.3});
// Map.addLayer(image, imageVisParam, 'True colour image');
var classNames = Mangrove.merge(Shrimp).merge(Residence).merge(Water).merge(Agriculture).merge(Other).merge(Evergreen);
//print(classNames);
var bands = L8col.bandNames();
var training = L8col.select(bands).sampleRegions({
  collection: classNames,
  properties: ['landcover'],
  scale: 30
});
//print(training);
var classifier = ee.Classifier.randomForest(100).train({
  features: training,
  classProperty: 'landcover',
  inputProperties: bands
});
print(classifier.explain());

//Run the classification
var classified = L8col.select(bands).classify(classifier);
//Display classification
Map.centerObject(classNames, 11);
Map.addLayer(classified,
{min: 1, max: 7, palette: ['#98ff00','#0b4a8b','#ffc82d','#00ffff','#bf04c2','#ff0000','#008800']},
'classification');

/*
//ACCURACY ASSESSMENT:
var withRandom = training.randomColumn();
// Approximately 50% of our training data
var trainingPartition = withRandom.filter(ee.Filter.lt('random', rate));
// Approximately 50% of our training data
var testingPartition = withRandom.filter(ee.Filter.gte('random', rate));
// Classification with Random Forest
var classifier = ee.Classifier.smileRandomForest(tree).train({
  features: trainingPartition, 
  classProperty: 'landcover', 
  inputProperties: bands,
});
// print(classifier.explain());
var classified = image.classify(classifier);
// Define a palette for the IGBP classification.
Map.addLayer(classified, {min: 1, max: 20, palette: igbpPalette}, 'S');
// var train = trainingPartition.classify(classifier);
*/

/*var test = training.classify(classifier);
// print(test);
var confMatrix = test.errorMatrix('landcover', 'classification');
var OA = confMatrix.accuracy()
var CA = confMatrix.consumersAccuracy()
var Kappa = confMatrix.kappa()
var Order = confMatrix.order()
var PA = confMatrix.producersAccuracy()
var exportAccuracy = ee.Feature(null, {matrix: confMatrix.array()})
// // Export the FeatureCollection.
// Export.table.toDrive({
//   collection: ee.FeatureCollection(exportAccuracy),
//   description: 'exportAccuracy_S',
//   fileFormat: 'CSV'
// });
// print(confMatrix,'Confusion Matrix South')
print(OA,'Overall Accuracy')
// print(CA,'Consumers Accuracy')
print(Kappa,'Kappa')
// print(Order,'Order')
// print(PA,'Producers Accuracy')


//Export the image
Export.image.toDrive({
  image: classified,
  maxPixels: 1e13,
  region: ThaiBinh,
  folder: 'GEE',
  scale: 100});
*/
//Add legend
var panel = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '5px;'
  }
})

var title = ui.Label({
  value: 'Classification',
  style: {
    fontSize: '14px',
    fontWeight: 'bold',
    margin: '0px;'
  }
})

panel.add(title)

var color = ['#98ff00','#0b4a8b','#ffc82d','#00ffff','#bf04c2','#ff0000','#008800']
var lc_class = ['Mangrove', 'Shrimp', 'Residence', 'Water','Agriculture','Other','Evergreen']

var list_legend = function(color, description) {
  
  var c = ui.Label({
    style: {
      backgroundColor: color,
      padding: '10px',
      margin: '4px'
    }
  })
  
  var ds = ui.Label({
    value: description,
    style: {
      margin: '5px'
    }
  })
  
  return ui.Panel({
    widgets: [c, ds],
    layout: ui.Panel.Layout.Flow('horizontal')
  })
}

for(var a = 0; a < 7; a++){
  panel.add(list_legend(color[a], lc_class[a]))
}

Map.add(panel)




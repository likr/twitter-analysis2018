const path = require('path')

const options = {
  module: {
    rules: [
    ]
  },
  entry: {
    bundle: './src/index'
  },
  output: {
    path: path.resolve(__dirname, 'public'),
    filename: '[name].js'
  },
  externals: {
  },
  plugins: [
  ],
  resolve: {
    extensions: ['.js']
  },
  devServer: {
    contentBase: path.join(__dirname, 'public'),
    historyApiFallback: true,
    port: 8080
  },
  node: {
    fs: 'empty'
  }
}

if (process.env.NODE_ENV !== 'production') {
  Object.assign(options, {
    devtool: 'inline-source-map'
  })
}

module.exports = options

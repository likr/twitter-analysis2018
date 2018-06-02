const path = require('path')
const CopyWebpackPlugin = require('copy-webpack-plugin')

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
    new CopyWebpackPlugin([
      {
        from: 'node_modules/bulma/css/bulma.css',
        to: 'vendor'
      }
    ])
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
  },
  optimization: {
    minimize: false
  }
}

if (process.env.NODE_ENV !== 'production') {
  Object.assign(options, {
    devtool: 'inline-source-map'
  })
}

module.exports = options

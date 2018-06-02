import '@webcomponents/custom-elements'
import 'eg-renderer'
import 'eg-renderer-ogdf'
import * as d3 from 'd3'

const wrapper = document.getElementById('wrapper')
const renderer = document.getElementById('renderer')
window.customElements.whenDefined('eg-renderer-ogdf').then(() => {
  renderer.width = wrapper.clientWidth
  renderer.height = wrapper.clientHeight

  window.addEventListener('resize', () => {
    renderer.width = wrapper.clientWidth
    renderer.height = wrapper.clientHeight
  })

  renderer.addEventListener('datafetchend', (event) => {
    const data = event.detail

    data.nodes.map((node, i) => {
      node.index = i
    })

    const sourceNodes = new Set()
    for (const {source} of data.links) {
      sourceNodes.add(source)
    }

    const degree = new Map(data.nodes.map(({index}) => [index, 0]))
    const outDegree = new Map(Array.from(sourceNodes).map((index) => [index, 0]))
    for (const {source, target, weight} of data.links) {
      degree.set(source, degree.get(source) + weight)
      degree.set(target, degree.get(target) + weight)
      outDegree.set(source, outDegree.get(source) + weight)
    }

    const nodeSizeMin = 350
    const nodeSizeMax = 2000
    const nodeFontSizeMin = 1000
    const nodeFontSizeMax = 2000
    const linkWidthMin = 10
    const linkWidthMax = 100
    const linkOpacityMin = 0.8
    const linkOpacityMax = 1
    const nodeSizeScale = d3.scaleLinear()
      .domain(d3.extent(data.nodes.map(({index}) => degree.get(index))))
      .range([nodeSizeMin, nodeSizeMax])
    const nodeFontSizeScale = d3.scaleLinear()
      .domain(d3.extent(Array.from(sourceNodes).map((index) => outDegree.get(index))))
      .range([nodeFontSizeMin, nodeFontSizeMax])
    const nodeColorScale = d3.scaleOrdinal(d3.schemeCategory10)
    const linkStrokeWidthScale = d3.scaleSqrt()
      .domain(d3.extent(data.links.map(({weight}) => weight)))
      .range([linkWidthMin, linkWidthMax])
    const linkStrokeOpacityScale = d3.scaleSqrt()
      .domain(d3.extent(data.links.map(({weight}) => weight)))
      .range([linkOpacityMin, linkOpacityMax])
    nodeColorScale(0)
    nodeColorScale(1)
    nodeColorScale(2)
    nodeColorScale(-1)

    for (const node of data.nodes) {
      node.width = nodeSizeScale(degree.get(node.index))
      node.height = nodeSizeScale(degree.get(node.index))
      node.fillColor = nodeColorScale(node.cluster)
      // node.fillOpacity = node.cluster === -1 ? 0 : 1
      // node.fillOpacity = sourceNodes.has(node.index) ? 1 : 0
      node.labelFillColor = nodeColorScale(node.cluster)
      if (!sourceNodes.has(node.index)) {
        node.label = ''
      } else {
        node.labelFontSize = nodeFontSizeScale(outDegree.get(node.index))
      }
    }

    for (const link of data.links) {
      link.strokeWidth = linkStrokeWidthScale(link.weight)
      link.strokeOpacity = linkStrokeOpacityScale(link.weight)
      // link.strokeOpacity = (data.nodes[link.source].cluster === -1) || (data.nodes[link.target].cluster === -1) ? 0 : 1
      // link.strokeOpacity = sourceNodes.has(link.source) && sourceNodes.has(link.target) ? 0.2 : 0
    }

    for (const key of data.graph.groups) {
      const nodes = data.nodes.filter((node) => node[key])
      const links = data.links.filter((link) => link[key])

      const degree = new Map(nodes.map(({index}) => [index, 0]))
      const outDegree = new Map(Array.from(sourceNodes).map((index) => [index, 0]))
      for (const {source, target, weight} of links) {
        degree.set(source, degree.get(source) + weight)
        degree.set(target, degree.get(target) + weight)
        outDegree.set(source, outDegree.get(source) + weight)
      }

      const nodeSizeScale = d3.scaleLinear()
        .domain(d3.extent(nodes.map(({index}) => degree.get(index))))
        .range([nodeSizeMin, nodeSizeMax])
      const nodeFontSizeScale = d3.scaleLinear()
        .domain(d3.extent(Array.from(sourceNodes).map((index) => outDegree.get(index))))
        .range([nodeFontSizeMin, nodeFontSizeMax])
      const linkStrokeWidthScale = d3.scaleLinear()
        .domain(d3.extent(links.map(({weight}) => weight)))
        .range([linkWidthMin, linkWidthMax])

      for (const node of nodes) {
        node[`width-${key}`] = nodeSizeScale(degree.get(node.index))
        node[`height-${key}`] = nodeSizeScale(degree.get(node.index))
        node[key] = node[key] ? 1 : 0
        if (sourceNodes.has(node.index)) {
          node[`labelFontSize-${key}`] = nodeFontSizeScale(outDegree.get(node.index))
        }
      }
      for (const link of links) {
        link[`strokeWidth-${key}`] = linkStrokeWidthScale(link.weight)
      }
    }

    const minDegree = 5
    data.links = data.links.filter(({source, target}) => degree.get(source) >= minDegree && degree.get(target) >= minDegree)
    data.nodes = data.nodes.filter(({index}) => degree.get(index) >= minDegree)

    const select = document.getElementById('key')
    for (const key of data.graph.groups) {
      const e = document.createElement('option')
      e.setAttribute('value', key)
      e.textContent = key
      select.appendChild(e)
    }
  })

  const reset = () => {
    document.getElementById('current').textContent = 'all'
    renderer.nodeWidthProperty = 'width'
    renderer.nodeHeightProperty = `height`
    renderer.nodeFillOpacityProperty = 'none'
    renderer.nodeLabelFillOpacityProperty = 'none'
    renderer.nodeLabelStrokeOpacityProperty = 'none'
    renderer.nodeLabelFontSizeProperty = `labelFontSize`
    renderer.linkVisibilityProperty = 'none'
    renderer.linkStrokeWidthProperty = 'strokeWidth'
  }

  const setKey = (key) => {
    document.getElementById('current').textContent = key
    renderer.nodeWidthProperty = `width-${key}`
    renderer.nodeHeightProperty = `height-${key}`
    renderer.nodeFillOpacityProperty = key
    renderer.nodeLabelFillOpacityProperty = key
    renderer.nodeLabelStrokeOpacityProperty = key
    renderer.nodeLabelFontSizeProperty = `labelFontSize-${key}`
    renderer.linkVisibilityProperty = key
    renderer.linkStrokeWidthProperty = `strokeWidth-${key}`
  }

  document.getElementById('center').addEventListener('click', () => {
    renderer.center()
  })

  document.getElementById('start').addEventListener('click', () => {
    renderer.autoCentering = false
    const keys = renderer.data.graph.groups
    let index = 0
    const id = setInterval(() => {
      if (index === keys.length) {
        reset()
        clearInterval(id)
      } else {
        const key = keys[index]
        setKey(key)
        index += 1
      }
    }, 1000)
  })

  document.getElementById('key').addEventListener('change', (event) => {
    const key = event.target.value
    if (key === 'all') {
      reset()
    } else {
      setKey(key)
    }
  })
})

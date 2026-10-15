import React, { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import * as echarts from 'echarts'
import type { SeriesData } from '../../types/dashboard'
import { axisStyle, commonChartTheme } from './chartUtils'

interface GdpChartProps {
  series: SeriesData[]
}

export const GdpChart: React.FC<GdpChartProps> = ({ series }) => {
  const option = useMemo(() => {
    const indSeries = series.find(
      (s) => s.key === 'IND' || s.label.toLowerCase().includes('india')
    )
    const wldSeries = series.find(
      (s) => s.key === 'WLD' || s.label.toLowerCase().includes('world')
    )

    // Collect all x categories (years)
    const categories = Array.from(
      new Set([
        ...(indSeries?.points.map((p) => p.x) || []),
        ...(wldSeries?.points.map((p) => p.x) || []),
      ])
    ).sort()

    const indData = categories.map((cat) => {
      const pt = indSeries?.points.find((p) => p.x === cat)
      return pt?.y ?? null
    })

    const wldData = categories.map((cat) => {
      const pt = wldSeries?.points.find((p) => p.x === cat)
      return pt?.y ?? null
    })

    return {
      ...commonChartTheme,
      legend: {
        ...commonChartTheme.legend,
        data: ['India', 'World'],
      },
      xAxis: {
        type: 'category',
        data: categories,
        ...axisStyle,
      },
      yAxis: {
        type: 'value',
        ...axisStyle,
        axisLabel: {
          ...axisStyle.axisLabel,
          formatter: '{value}%',
        },
      },
      series: [
        {
          name: 'India',
          type: 'bar',
          data: indData,
          barMaxWidth: 24,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#0fb8e6' },
              { offset: 1, color: '#005691' },
            ]),
          },
          label: {
            show: true,
            position: 'top',
            color: '#0fb8e6',
            fontSize: 11,
            formatter: (params: { value: number | null }) =>
              params.value !== null ? `${params.value}%` : '—',
          },
        },
        {
          name: 'World',
          type: 'bar',
          data: wldData,
          barMaxWidth: 24,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#ffa73f' },
              { offset: 1, color: '#a65100' },
            ]),
          },
          label: {
            show: true,
            position: 'top',
            color: '#ffa73f',
            fontSize: 11,
            formatter: (params: { value: number | null }) =>
              params.value !== null ? `${params.value}%` : '—',
          },
        },
      ],
    }
  }, [series])

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '290px' }}>
      <ReactECharts
        option={option}
        style={{ width: '100%', height: '100%', minHeight: '290px' }}
        opts={{ renderer: 'canvas' }}
        notMerge={true}
      />
    </div>
  )
}

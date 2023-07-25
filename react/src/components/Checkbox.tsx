import React, { useState } from "react"
import Stack, { StackDirection } from "./Stack"
import Label, { LabelSize } from "./Label"

type CheckboxProps = {
    label: string
    className?: string
    defaultState: boolean
    stateOverride?: boolean
    onClick?: () => void
}

const Checkbox: React.FC<CheckboxProps> = ({
    label,
    className,
    defaultState,
    stateOverride,
    onClick,
}) => {
    const [state, setState] = useState(defaultState)
    return (
        <Stack direction={StackDirection.Horizontal}>
            <Label
                size={LabelSize.Medium}
                className={`mr-8 ${className} whitespace-nowrap`}
            >
                {label}
            </Label>
            <input
                type="checkbox"
                defaultChecked={state}
                onClick={e => {
                    setState((e.target as HTMLInputElement).checked)
                    if (onClick) onClick()
                }}
                className="bg-gray-500 translate-y-1/4 duration-200 cursor-pointer appearance-none w-5 h-5 rounded-full checked:bg-gradient-to-br checked:from-red-700 checked:to-orange-400"
                checked={stateOverride != null ? stateOverride : state}
            />
        </Stack>
    )
}

export default Checkbox
